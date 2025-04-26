from django.urls import path, include
from . import views
from .views import PatientViewSet, ProgramViewSet, EnrollmentViewSet, DiagnosisViewSet
from rest_framework import routers


router = routers.DefaultRouter()
router.register(r'patients', PatientViewSet)
router.register(r'programs', ProgramViewSet)
router.register(r'enrollments', EnrollmentViewSet)
router.register(r'diagnoses', DiagnosisViewSet)




app_name = 'health_app'


urlpatterns = [
    path('api/', include(router.urls)),
    path('',                                  views.role_redirect,     name='role_redirect'),
    path('patients/',                         views.list_patients,     name='list_patients'),
    path('patients/create/',                  views.create_patient,    name='create_patient'),
    path('enrollments/',                      views.list_enrollments,  name='list_enrollments'),   
    path('enrollments/create/',               views.create_enrollment, name='create_enrollment'),
    path('doctor/patients/',                  views.doctor_patients,   name='doctor_patients'),
    path('doctor/diagnose/',                  views.create_diagnosis,  name='create_diagnosis'),
    path('pharmacy/queue/',                   views.pharmacy_queue,    name='pharmacy_queue'),
    path('pharmacy/dispense/<int:diag_id>/<int:enrollment_id>/',views.dispense, name='dispense'),
    path('overview/', views.admin_overview, name='admin_overview'),
    path('accounts/',                         include('django.contrib.auth.urls')),

]
