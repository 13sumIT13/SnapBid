from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path(r"ws/", consumers.BidConsumer.as_asgi()),
    path(r"ws/timer/", consumers.TimerStatusConsumer.as_asgi()),
]