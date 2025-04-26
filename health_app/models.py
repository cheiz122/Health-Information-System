from django.db import models
from django.conf import settings

class Program(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self): return self.name

class Patient(models.Model):
    GENDER_CHOICES = [('Male','Male'),('Female','Female'),('Other','Other')]
    name    = models.CharField(max_length=100)
    age     = models.PositiveIntegerField()
    gender  = models.CharField(max_length=10, choices=GENDER_CHOICES)
    contact = models.CharField(max_length=100, unique=True)
    def __str__(self): return f"{self.name} ({self.contact})"

class Enrollment(models.Model):
    patient     = models.ForeignKey(Patient, related_name='enrollments', on_delete=models.CASCADE)
    program     = models.ForeignKey(Program, on_delete=models.CASCADE)
    enrolled_on = models.DateField(auto_now_add=True)
    STATUS_CHOICES = [('registered','Registered'),('consulted','Consulted'),('dispensed','Medicated')]
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='registered')
    def __str__(self): return f"{self.patient.name} → {self.program.name}"

class DoctorProfile(models.Model):
    user    = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    def __str__(self): return f"Dr. {self.user.username} – {self.program.name}"

class Diagnosis(models.Model):
    enrollment      = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    diagnosis       = models.TextField()
    recommendations = models.TextField()
    created_on      = models.DateTimeField(auto_now_add=True)
    created_by      = models.ForeignKey(settings.AUTH_USER_MODEL,
                                      null=True, on_delete=models.SET_NULL,
                                      related_name='diagnoses_created')
    dispensed       = models.BooleanField(default=False)
    dispensed_on    = models.DateTimeField(null=True, blank=True)
    dispensed_by    = models.ForeignKey(settings.AUTH_USER_MODEL,
                                      null=True, blank=True, on_delete=models.SET_NULL,
                                      related_name='dispensations')
    def __str__(self): return f"Diagnosis #{self.id} for {self.enrollment.patient.name}"
