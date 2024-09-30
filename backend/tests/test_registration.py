from pydantic_core import ErrorDetails
import pytest
from django.urls import reverse
from rest_framework import status
from django.test import override_settings

# @override_settings(REST_FRAMEWORK={'DEFAULT_THROTTLE_RATES': {'register': '1000/minute'}})
@pytest.mark.django_db
def test_user_registration(api_client):
    url = reverse('register')  # Adjust to your registration endpoint
    data = {
        'email': 'testuser@example.com',
        'password': 'strong_password',
        'role': 'vendor'
    }
    response = api_client.post(url, data)
    
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['message'] == "User registered successfully"

# @override_settings(REST_FRAMEWORK={'DEFAULT_THROTTLE_RATES': {'register': '1000/minute'}})
@pytest.mark.django_db
def test_registration_password_mismatch(api_client):
    url = reverse('register')
    data = {
        'email': 'testuser2@example.com',
        'password': 'password123',
        'role': 'password456'
    }
    response = api_client.post(url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
