from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from .models import User, Expense, ExpenseSplit


class UserTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_user(self):
        user_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "mobile": "1234567890"
        }
        response = self.client.post('/api/users/', user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().name, 'John Doe')
