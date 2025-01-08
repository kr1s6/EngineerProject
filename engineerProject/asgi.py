import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from webStore.routing import websocket_urlpatterns  # Upewnij się, że ścieżka jest poprawna

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'engProject.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns  # Odwołanie do routingu WebSocketów
        )
    ),
})
