import pytest
from django.urls import reverse
from rest_framework import status

@pytest.mark.django_db
def test_password_reset_request(api_client, create_user):
    user = create_user(email='testreset@example.com', password='oldpassword')
    url = reverse('password-reset-request')  # Adjust to your password reset endpoint
    data = {'email': user.email}
    response = api_client.post(url, data)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['message'] == 'Password reset link has been sent'


@pytest.mark.django_db
def test_password_reset_invalid_email(api_client):
    url = reverse('password-reset-request')
    data = {'email': 'nonexisting@example.com'}
    response = api_client.post(url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'email' in response.data
