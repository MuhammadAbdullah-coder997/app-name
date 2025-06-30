from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from .models import Reading

# Create your tests here.

class AdminTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.superuser = get_user_model().objects.create_superuser(
            email="admin@example.com",
            password="admin123"
        )
        self.client.login(email="admin@example.com", password="admin123")
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            password="test123"
        )
        self.reading = Reading.objects.create(
            user=self.user,
            systolic=120,
            diastolic=80,
            glucose_level=100.0,
            glucose_unit="mg/dL"
        )

    def test_user_admin_list_display(self):
        response = self.client.get('/admin/myapp/user/')
        self.assertContains(response, "test@example.com")
        self.assertContains(response, "test123")  # Assuming get_full_name returns email if no name

    def test_reading_admin_list_display(self):
        response = self.client.get('/admin/myapp/reading/')
        self.assertContains(response, "120/80")
        self.assertContains(response, "Normal")  # From get_blood_pressure_category