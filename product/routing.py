from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path(r"ws/", consumers.BidConsumer.as_asgi()),
]