import pytest
from django.urls import reverse
from rest_framework import status
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator

@pytest.mark.django_db
def test_email_verification(api_client, create_user):
    user = create_user(email='verifyuser@example.com', password='password123', is_active=False)

    token_generator = PasswordResetTokenGenerator()
    uid = urlsafe_base64_encode(force_bytes(user.pk))  # Encode user ID to bytes and then base64
    token = token_generator.make_token(user)  # Adjust based on your token generator logic

    url = reverse('email-verify', kwargs={'uidb64': uid, 'token': token})
        # url = reverse('email-verify', kwargs={'uidb64': 'uidb64','token': 'dummy_token'})  # Adjust to your email verification endpoint
    response = api_client.post(url)

    assert response.status_code == status.HTTP_200_OK
    assert 'Email verified successfully' in response.data
