import pytest
from django.urls import reverse
from rest_framework import status

# @pytest.mark.django_db
# def test_rate_limit_on_password_reset(api_client, create_user):
#     user = create_user(email='ratelimit@example.com', password='password123')
#     url = reverse('password-reset-request')
#     data = {'email': user.email}

#     # Simulate multiple requests to trigger rate limiting
#     for _ in range(5):
#         response = api_client.post(url, data)

#     assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
#     assert 'Request was throttled' in response.data['detail']

