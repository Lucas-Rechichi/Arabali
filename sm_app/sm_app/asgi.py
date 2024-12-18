"""
ASGI config for sm_app project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import main.routing
import messaging.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sm_app.settings')
# configures the ASGI application and connects our routing urls to the application
application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            main.routing.websocket_urlpatterns +
            messaging.routing.websocket_urlpatterns
        )
    ),
})
