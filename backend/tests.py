from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Application, Job, Resume


class PublicApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_health_endpoint_returns_ok(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')

    def test_registration_creates_user_with_hashed_password(self):
        response = self.client.post(
            '/api/register/',
            {
                'username': 'applicant',
                'email': 'applicant@example.com',
                'password': 'correct-horse-battery',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        user = User.objects.get(username='applicant')
        self.assertTrue(user.check_password('correct-horse-battery'))

    def test_job_filter_matches_location_without_case_sensitivity(self):
        recruiter = User.objects.create_user(username='recruiter', password='test-password')
        Job.objects.create(
            recruiter=recruiter,
            title='Engineer',
            description='Build web applications.',
            company='Example Studio',
            location='New York',
            job_type='Full-time',
        )

        response = self.client.get('/api/jobs/?location=new')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['location'], 'New York')

    def test_jobs_api_allows_local_react_origin(self):
        response = self.client.get(
            '/api/jobs/',
            HTTP_ORIGIN='http://127.0.0.1:3000',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response['Access-Control-Allow-Origin'],
            'http://127.0.0.1:3000',
        )


class ApplicationsApiTests(TestCase):
    def test_my_applications_returns_job_details_for_signed_in_user(self):
        recruiter = User.objects.create_user(username='recruiter', password='test-password')
        applicant = User.objects.create_user(username='applicant', password='test-password')
        job = Job.objects.create(
            recruiter=recruiter,
            title='Frontend Engineer',
            description='Build web applications.',
            company='Example Studio',
            location='Remote',
            job_type='Full-time',
        )
        resume = Resume.objects.create(user=applicant, file='resumes/applicant.pdf')
        Application.objects.create(applicant=applicant, job=job, resume=resume)

        client = APIClient()
        client.force_authenticate(user=applicant)
        response = client.get('/api/my-applications/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]['job']['title'], 'Frontend Engineer')
        self.assertEqual(response.data[0]['job']['company'], 'Example Studio')
