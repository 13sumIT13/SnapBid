from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path("ws/bid/<int:auction_id>/", consumers.BidConsumer.as_asgi()),
    path(r"ws/timer/<int:auction_id>/", consumers.TimerStatusConsumer.as_asgi()),
]