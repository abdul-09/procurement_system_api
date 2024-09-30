import pytest
from django.urls import reverse
from rest_framework import status

@pytest.mark.django_db
def test_login_success(api_client, create_user):
    user = create_user(email='testlogin@example.com', password='testpassword')
    url = reverse('user-login')  # Adjust to your token login URL
    data = {
        'email': user.email,
        'password': 'testpassword'
    }
    response = api_client.post(url, data)

    assert response.status_code == status.HTTP_200_OK
    assert 'access' in response.data

@pytest.mark.django_db
def test_login_invalid_credentials(api_client):
    url = reverse('user-login')
    data = {
        'email': 'nonexistinguser@example.com',
        'password': 'wrongpassword'
    }
    response = api_client.post(url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'Invalid login credentials' in response.data['non_field_errors'][0]
