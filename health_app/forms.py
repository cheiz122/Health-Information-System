from django import forms
from django.core.exceptions import ValidationError
import requests
from .models import Patient, Enrollment, Diagnosis

API = 'http://127.0.0.1:8000/api'

class PatientForm(forms.Form):
    name    = forms.CharField(max_length=100)
    age     = forms.IntegerField(min_value=0)
    gender  = forms.ChoiceField(choices=Patient.GENDER_CHOICES)
    contact = forms.CharField(max_length=100)

    def clean_contact(self):
        contact = self.cleaned_data['contact']
        if Patient.objects.filter(contact=contact).exists():
            raise ValidationError('Patient with this contact already exists.')
        return contact  



class EnrollmentForm(forms.Form):
    patient       = forms.ChoiceField(choices=[])
    program       = forms.ChoiceField(choices=[])
    date_enrolled = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Load patients
        r = requests.get(f"{API}/patients/")
        if r.ok:
            self.fields['patient'].choices = [(p['id'], p['name']) for p in r.json()]
        # Load programs
        r2 = requests.get(f"{API}/programs/")
        if r2.ok:
            self.fields['program'].choices = [(p['id'], p['name']) for p in r2.json()]

class DiagnosisForm(forms.Form):
    enrollment      = forms.ChoiceField(choices=[])
    diagnosis       = forms.CharField(widget=forms.Textarea)
    recommendations = forms.CharField(widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [(e.id, f"{e.patient.name} - {e.program.name}") 
                   for e in Enrollment.objects.filter(status='registered')]
        self.fields['enrollment'].choices = choices

    def clean_enrollment(self):
        eid = int(self.cleaned_data['enrollment'])
        if Diagnosis.objects.filter(enrollment_id=eid).exists():
            raise ValidationError('Diagnosis already exists for this enrollment.')
        return eid
