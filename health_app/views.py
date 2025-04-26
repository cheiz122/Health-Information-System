
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required


import requests
from django.shortcuts               import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils.timezone          import now
from django.utils.dateparse         import parse_date
from django.db.models               import Count

from rest_framework               import viewsets, filters
from rest_framework.decorators    import action
from rest_framework.response      import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models      import Program, Patient, Enrollment, DoctorProfile, Diagnosis
from .forms       import PatientForm, EnrollmentForm
from .serializers import (
    ProgramSerializer,
    PatientSerializer,
    EnrollmentSerializer,
    DiagnosisSerializer,
)

# ────────────────────────────────────────────────────────────────────────────────
# API ENDPOINT CONSTANTS (used by your function-based views)
# ────────────────────────────────────────────────────────────────────────────────

API_BASE    = 'http://127.0.0.1:8000/api/'
PATIENT_API = f'{API_BASE}patients/'
ENROLL_API  = f'{API_BASE}enrollments/'
DIAG_API    = f'{API_BASE}diagnoses/'

# ────────────────────────────────────────────────────────────────────────────────
# ROLE‐CHECK DECORATOR
# ────────────────────────────────────────────────────────────────────────────────

def in_group(name):
    """
    Decorator: allows only users in the given group (or superusers).
    """
    return user_passes_test(lambda u: u.groups.filter(name=name).exists() or u.is_superuser)

# ────────────────────────────────────────────────────────────────────────────────
# DRF VIEWSETS
# ────────────────────────────────────────────────────────────────────────────────

class ProgramViewSet(viewsets.ModelViewSet):
    """API CRUD for Program."""
    queryset         = Program.objects.all()
    serializer_class = ProgramSerializer

class PatientViewSet(viewsets.ModelViewSet):
    """API CRUD for Patient, with nested enrollments and filtering."""
    queryset         = Patient.objects.prefetch_related('enrollments__program').all()
    serializer_class = PatientSerializer
    filter_backends  = [DjangoFilterBackend, filters.SearchFilter]
    search_fields    = ['name', 'contact']

    def get_queryset(self):
        qs = super().get_queryset()
        contact    = self.request.query_params.get('contact')
        date       = self.request.query_params.get('date')
        month      = self.request.query_params.get('month')
        year       = self.request.query_params.get('year')
        program_id = self.request.query_params.get('program_id')

        if contact:
            qs = qs.filter(contact__icontains=contact)
        if date:
            try:
                qs = qs.filter(enrollments__enrolled_on=parse_date(date))
            except ValueError:
                pass
        if month:
            qs = qs.filter(enrollments__enrolled_on__month=month)
        if year:
            qs = qs.filter(enrollments__enrolled_on__year=year)
        if program_id:
            qs = qs.filter(enrollments__program_id=program_id)

        return qs.distinct()

    @action(detail=True, methods=['get'])
    def profile(self, request, pk=None):
        """GET /api/patients/{pk}/profile/ → full patient data."""
        patient    = self.get_object()
        serializer = self.get_serializer(patient)
        return Response(serializer.data)

class EnrollmentViewSet(viewsets.ModelViewSet):
    """API CRUD for Enrollment."""
    queryset         = Enrollment.objects.select_related('patient', 'program').all()
    serializer_class = EnrollmentSerializer

class DiagnosisViewSet(viewsets.ModelViewSet):
    """API CRUD for Diagnosis."""
    queryset         = Diagnosis.objects.select_related('enrollment__patient').all()
    serializer_class = DiagnosisSerializer

# ────────────────────────────────────────────────────────────────────────────────
# ROLE‐BASED REDIRECT & SUPERUSER DASHBOARD
# ────────────────────────────────────────────────────────────────────────────────

@login_required
def role_redirect(request):
    """
    After login, send user to their landing page based on role.
    """
    u = request.user
    if u.is_superuser:
        return redirect('health_app:admin_overview')
    if u.groups.filter(name='Receptionist').exists():
        return redirect('health_app:list_patients')
    if u.groups.filter(name='Doctor').exists():
        return redirect('health_app:doctor_patients')
    if u.groups.filter(name='Pharmacist').exists():
        return redirect('health_app:pharmacy_queue')
    # Fallback
    return redirect('health_app:login')
class CustomLoginView(LoginView):
    """
    Overrides the default LoginView to redirect user
    based on role after login.
    """
    def get_success_url(self):
        return reverse_lazy('health_app:role_redirect')

@login_required
@in_group('Admin')  # or just superuser
def dashboard(request):
    """
    Superuser/Admin overview counts.
    """
    total_patients    = Patient.objects.count()
    total_enrollments = Enrollment.objects.count()
    total_diagnoses   = Diagnosis.objects.count()
    total_dispensed   = Diagnosis.objects.filter(dispensed=True).count()
    total_pending     = Diagnosis.objects.filter(dispensed=False).count()

    return render(request, 'health_app/dashboard.html', {
        'total_patients':    total_patients,
        'total_enrollments': total_enrollments,
        'total_diagnoses':   total_diagnoses,
        'total_dispensed':   total_dispensed,
        'total_pending':     total_pending,
    })

# ────────────────────────────────────────────────────────────────────────────────
# RECEPTIONIST VIEWS
# ────────────────────────────────────────────────────────────────────────────────

@login_required
@in_group('Receptionist')
def list_patients(request):
    """
    List patients via API, with optional search (?q=).
    """
    q       = request.GET.get('q', '')
    params  = {'search': q} if q else {}
    resp    = requests.get(PATIENT_API, params=params)
    patients = resp.json() if resp.ok else []
    return render(request, 'health_app/patients/list.html', {
        'patients': patients,
        'q':        q,
    })

@login_required
@in_group('Receptionist')
def create_patient(request):
    """
    Form to create a patient → POST to /api/patients/.
    """
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            r = requests.post(PATIENT_API, json=form.cleaned_data)
            if r.status_code == 201:
                return render(request, 'health_app/receipts/patient_receipt.html', {
                    'patient': r.json()
                })
            form.add_error(None, 'API error: ' + r.text)
    else:
        form = PatientForm()
    return render(request, 'health_app/patients/create.html', {'form': form})

@login_required
@in_group('Receptionist')
def list_enrollments(request):
    """
    List enrollments via API, with optional search (?q=).
    """
    q           = request.GET.get('q', '')
    params      = {'search': q} if q else {}
    resp        = requests.get(ENROLL_API, params=params)
    enrollments = resp.json() if resp.ok else []
    return render(request, 'health_app/enrollments/list.html', {
        'enrollments': enrollments,
        'q':           q,
    })

@login_required
@in_group('Receptionist')
def create_enrollment(request):
    """
    Form to create an enrollment → POST to /api/enrollments/.
    """
    if request.method == 'POST':
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            data = {
                'patient':     int(form.cleaned_data['patient']),
                'program':     int(form.cleaned_data['program']),
                'enrolled_on': form.cleaned_data['date_enrolled'].isoformat(),

            }
            r = requests.post(ENROLL_API, json=data)
            if r.status_code == 201:
                return redirect('health_app:list_enrollments')
            form.add_error(None, 'API error: ' + r.text)
    else:
        form = EnrollmentForm()
    return render(request, 'health_app/enrollments/create.html', {'form': form})

# ────────────────────────────────────────────────────────────────────────────────
# DOCTOR VIEWS
# ────────────────────────────────────────────────────────────────────────────────

@login_required
@in_group('Doctor')
def doctor_patients(request):
    """
    List patients enrolled in the logged-in doctor's program.
    """
    q  = request.GET.get('q', '')
    dp = get_object_or_404(DoctorProfile, user=request.user)
    patients = Patient.objects.filter(
        enrollments__program=dp.program,
        name__icontains=q
    ).distinct()
    return render(request, 'health_app/doctor/patients.html', {
        'patients': patients,
        'program':  dp.program,
        'q':        q,
    })

@login_required
@in_group('Doctor')
@in_group('Receptionist')
def view_patient(request, patient_id):
    """
    View patient details + relevant enrollments (Doctor or Receptionist).
    """
    resp = requests.get(f"{PATIENT_API}{patient_id}/")
    patient = resp.json() if resp.ok else None

    dp = get_object_or_404(DoctorProfile, user=request.user)
    enrollments = Enrollment.objects.filter(
        patient_id=patient_id,
        program=dp.program
    )

    return render(request, 'health_app/doctor/view_patient.html', {
        'patient':     patient,
        'enrollments': enrollments,
    })

@login_required
@in_group('Doctor')
def create_diagnosis(request, enrollment_id=None):
    """
    Form to create a Diagnosis → POST to /api/diagnoses/.
    Prevents duplicate diagnoses per enrollment.
    """
    dp    = get_object_or_404(DoctorProfile, user=request.user)
    error = None

    if request.method == 'POST':
        diag_text = request.POST.get('diagnosis', '').strip()
        recs      = request.POST.get('recommendations', '').strip()
        eid       = request.POST.get('enrollment')

        if diag_text and recs and eid:
            if Diagnosis.objects.filter(enrollment_id=eid).exists():
                error = "Diagnosis already exists for this enrollment."
            else:
                payload = {
                    'enrollment':      eid,
                    'diagnosis':       diag_text,
                    'recommendations': recs,
                    'created_by':      request.user.id,
                }
                r = requests.post(DIAG_API, json=payload)
                if r.status_code == 201:
                    # mark consulted via API
                    requests.patch(f"{ENROLL_API}{eid}/", json={'status': 'consulted'})
                    return render(request, 'health_app/receipts/diagnosis_receipt.html', {
                        'diagnosis': r.json()
                    })
                error = "API error saving diagnosis."
        else:
            error = "All fields are required."

    enrollments = Enrollment.objects.filter(program=dp.program, status='registered')
    return render(request, 'health_app/doctor/create_diagnosis.html', {
        'enrollments':            enrollments,
        'error':                  error,
        'selected_enrollment_id': enrollment_id,
    })

# ────────────────────────────────────────────────────────────────────────────────
# PHARMACIST VIEWS
# ────────────────────────────────────────────────────────────────────────────────

@login_required
@in_group('Pharmacist')
def pharmacy_queue(request):
    """
    Show undispensed vs. dispensed diagnoses.
    """
    undispensed = Diagnosis.objects.filter(dispensed=False) \
        .select_related('enrollment__patient', 'enrollment__program')
    dispensed   = Diagnosis.objects.filter(dispensed=True) \
        .select_related('enrollment__patient', 'enrollment__program')

    return render(request, 'health_app/pharmacy/queue.html', {
        'undispensed_diagnoses': undispensed,
        'dispensed_diagnoses':   dispensed,
    })

@login_required
@in_group('Pharmacist')
def dispense(request, diag_id, enrollment_id):
    """
    Mark a Diagnosis as dispensed and update its Enrollment status.
    """
    diag = get_object_or_404(Diagnosis, id=diag_id)
    diag.dispensed    = True
    diag.dispensed_on = now()
    diag.dispensed_by = request.user
    diag.save()

    enroll        = get_object_or_404(Enrollment, id=enrollment_id)
    enroll.status = 'dispensed'
    enroll.save()

    return render(request, 'health_app/receipts/dispense_receipt.html', {
        'diag': diag
    })

# ────────────────────────────────────────────────────────────────────────────────
# UTILITY VIEW: PATIENT LOOKUP
# ────────────────────────────────────────────────────────────────────────────────

def patient_lookup(request):
    """
    Find patient by contact, display their enrollments & diagnoses.
    """
    contact = request.GET.get('contact')
    patient = Patient.objects.filter(contact=contact).first()
    if patient:
        enrollments = patient.enrollments.select_related('program')
        diagnoses   = Diagnosis.objects.filter(enrollment__in=enrollments) \
                           .select_related('created_by')
        return render(request, 'health_app/patient_lookup.html', {
            'patient':     patient,
            'enrollments': enrollments,
            'diagnoses':   diagnoses
        })
    return render(request, 'health_app/patient_lookup.html', {'not_found': True})

# ────────────────────────────────────────────────────────────────────────────────
# STAFF‐ONLY ADMIN OVERVIEW
# ────────────────────────────────────────────────────────────────────────────────

@staff_member_required
def admin_overview(request):
    """
    Staff-only overview: model counts, program & doctor summaries, patient search.
    """
    patients_count      = Patient.objects.count()
    total_enrollments   = Enrollment.objects.count()
    programs_summary    = Enrollment.objects.values('program__name') \
                                .annotate(count=Count('id'))
    doctor_diagnoses    = Diagnosis.objects.values('created_by__username') \
                                .annotate(count=Count('id'))
    dispensed_count     = Diagnosis.objects.filter(dispensed=True).count()
    not_dispensed_count = Diagnosis.objects.filter(dispensed=False).count()

    contact = request.GET.get('contact')
    searched_patient = Patient.objects.filter(contact=contact).first() if contact else None

    return render(request, 'health_app/admin/overview.html', {
        'patients_count':      patients_count,
        'total_enrollments':   total_enrollments,
        'programs_summary':    programs_summary,
        'doctor_diagnoses':    doctor_diagnoses,
        'dispensed_count':     dispensed_count,
        'not_dispensed_count': not_dispensed_count,
        'searched_patient':    searched_patient,
    })
