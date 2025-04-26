from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from health_app.models import Patient, Program, Enrollment, Diagnosis
from rest_framework import status

class HealthAppTestCase(TestCase):
    """
    A test case class for testing the Health Application views, models, and urls.
    """

    def setUp(self):
        # Creating test data for models
        self.user = get_user_model().objects.create_user(username='testuser', password='password123')
        self.patient = Patient.objects.create(
            name='John Doe',
            id_number='12345678',
            phone='0700000000',
            email='johndoe@example.com'
        )
        self.program = Program.objects.create(name='Health Program 1')
        self.enrollment = Enrollment.objects.create(patient=self.patient, program=self.program)
        self.diagnosis = Diagnosis.objects.create(patient=self.patient, diagnosis='Flu')

        # URLs for views
        self.patient_url = reverse('health_app:patient_detail', kwargs={'pk': self.patient.pk})
        self.program_url = reverse('health_app:program_detail', kwargs={'pk': self.program.pk})
        self.enrollment_url = reverse('health_app:enrollment_detail', kwargs={'pk': self.enrollment.pk})

    def test_patient_model(self):
        """
        Test the Patient model.
        """
        patient = self.patient
        self.assertEqual(patient.name, 'John Doe')
        self.assertEqual(patient.id_number, '12345678')
        self.assertEqual(patient.phone, '0700000000')
        self.assertEqual(patient.email, 'johndoe@example.com')

    def test_program_model(self):
        """
        Test the Program model.
        """
        program = self.program
        self.assertEqual(program.name, 'Health Program 1')

    def test_enrollment_model(self):
        """
        Test the Enrollment model.
        """
        enrollment = self.enrollment
        self.assertEqual(enrollment.patient.name, 'John Doe')
        self.assertEqual(enrollment.program.name, 'Health Program 1')

    def test_diagnosis_model(self):
        """
        Test the Diagnosis model.
        """
        diagnosis = self.diagnosis
        self.assertEqual(diagnosis.diagnosis, 'Flu')

    def test_patient_detail_view(self):
        """
        Test the patient detail view.
        """
        response = self.client.get(self.patient_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John Doe')

    def test_program_detail_view(self):
        """
        Test the program detail view.
        """
        response = self.client.get(self.program_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Health Program 1')

    def test_enrollment_detail_view(self):
        """
        Test the enrollment detail view.
        """
        response = self.client.get(self.enrollment_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John Doe')
        self.assertContains(response, 'Health Program 1')

    def test_patient_url_resolves(self):
        """
        Test if the patient URL resolves correctly.
        """
        response = self.client.get(f'/patients/{self.patient.pk}/')
        self.assertEqual(response.status_code, 200)

    def test_program_url_resolves(self):
        """
        Test if the program URL resolves correctly.
        """
        response = self.client.get(f'/programs/{self.program.pk}/')
        self.assertEqual(response.status_code, 200)

    def test_enrollment_url_resolves(self):
        """
        Test if the enrollment URL resolves correctly.
        """
        response = self.client.get(f'/enrollments/{self.enrollment.pk}/')
        self.assertEqual(response.status_code, 200)

    def test_api_patient_creation(self):
        """
        Test the creation of a patient through the API.
        """
        data = {
            'name': 'Jane Doe',
            'id_number': '87654321',
            'phone': '0711111111',
            'email': 'janedoe@example.com'
        }
        response = self.client.post(reverse('health_app:patient_list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Patient.objects.count(), 2)

    def test_api_program_creation(self):
        """
        Test the creation of a program through the API.
        """
        data = {'name': 'Health Program 2'}
        response = self.client.post(reverse('health_app:program_list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Program.objects.count(), 2)
