import json
from channels.generic.websocket import AsyncWebsocketConsumer
from notification.models import Notification
from asgiref.sync import sync_to_async
from django.db import models

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handle WebSocket connection."""

        self.user = self.scope["user"]
        if self.user.is_authenticated:
            self.room_name = f"user_{self.user.id}"
            await self.channel_layer.group_add(self.room_name, self.channel_name)
            await self.accept()

        else:
            await self.close()

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""

        if self.user.is_authenticated:
            await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):
        """Handle incoming WebSocket messages."""
        pass

    async def send_notification(self, event):
        """Send real-time notifications to clients."""
        notification = event.get('notification')  # Safely get the 'notification' key
        if notification is not None:
            notification['unread_notification'] = await self.get_unread_count()
            print(notification)
            await self.send(text_data=json.dumps(notification))

        else:
            # If 'notification' does not exist, send only the unread count
            unread_notification_count = event.get('unread_count', 0)  # Default to 0 if 'unread_count' is missing
            await self.send(text_data=json.dumps({'unread_notification': unread_notification_count}))
                
    @sync_to_async
    def get_unread_count(self):
        """Fetch unread notifications count asynchronously."""
        return Notification.objects.filter(user=self.user, is_read=False).count()
    
    