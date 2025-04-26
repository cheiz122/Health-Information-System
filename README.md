
# Health Information System

## Overview
The **Health Information System** is a comprehensive Django-based application designed to manage health data for patients, including their enrollment in various health programs, diagnoses, and treatments. The system is built with a focus on flexibility, scalability, and ease of use.

## Key Features
- **Patient Management**: Track patient information, including personal details and medical history.
- **Program Management**: Administer various health programs, such as consultations and treatments.
- **Enrollment Tracking**: Manage patient enrollments in different health programs.

## Project Structure

health_information_system/ ├── health_app/ # Main app containing models, views, and templates │ ├── migrations/ # Database migrations │ ├── models.py # Django models for Patient, Program, etc. │ ├── views.py # Views for handling user requests │ ├── serializers.py # Serializers for API responses │ ├── urls.py # URL routing for views │ └── templates/ # HTML templates for views │ ├── health_system/ # Project configuration │ ├── settings.py # Django settings │ ├── urls.py # URL routing for the entire project │ └── wsgi.py # WSGI configuration │ ├── manage.py # Django management script ├── requirements.txt # Project dependencies └── README.md #

API Endpoints
The Health Information System exposes the following API endpoints using Django Rest Framework:

1. Patients
GET /api/patients/ - List all patients

POST /api/patients/ - Create a new patient

GET /api/patients/{id}/ - Retrieve patient details

PUT /api/patients/{id}/ - Update patient details

2. Programs
GET /api/programs/ - List all health programs

POST /api/programs/ - Create a new health program

GET /api/programs/{id}/ - Retrieve program details

3. Enrollments
GET /api/enrollments/ - List all enrollments

POST /api/enrollments/ - Create a new enrollment

4. Diagnoses
GET /api/diagnoses/ - List all diagnoses

POST /api/diagnoses/ - Add a new diagnosis

5. Authentication
POST /api/token/ - Obtain JWT Token for authentication