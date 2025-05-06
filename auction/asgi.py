import os
import django
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auction.settings')
django.setup()  # <-- make sure apps are loaded before importing anything else

# Now it's safe to import routing, models, etc.
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from product import routing as product_routing
from notification import routing as notification_routing

websocket_urlpatterns = product_routing.websocket_urlpatterns + notification_routing.websocket_urlpatterns

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        ),
    }
)
