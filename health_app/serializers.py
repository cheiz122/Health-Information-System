from rest_framework import serializers
from .models import Program, Patient, Enrollment, Diagnosis

class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = '__all__'

class EnrollmentSerializer(serializers.ModelSerializer):
    diagnosis_id = serializers.SerializerMethodField()
    class Meta:
        model = Enrollment
        fields = '__all__'
    def get_diagnosis_id(self, obj):
        diag = obj.diagnosis_set.first()
        return diag.id if diag else None

class PatientSerializer(serializers.ModelSerializer):
    enrollments = EnrollmentSerializer(many=True, read_only=True)
    class Meta:
        model = Patient
        fields = ['id','name','age','gender','contact','enrollments']

class DiagnosisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diagnosis
        fields = '__all__'
