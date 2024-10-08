"""
ASGI config for procurement_system project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""


import os

import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.layers import get_channel_layer
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator



os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'procurement_system.settings')

django_application = get_asgi_application()
from api.routing import websocket_urlpatterns #noqa
from api.middleware import JwtAuthMiddlewareStack #noqa


application = ProtocolTypeRouter(
    {
        "http": django_application,
        "websocket":
        JwtAuthMiddlewareStack(
            URLRouter(
                websocket_urlpatterns
            )
        ),
    
    }
)