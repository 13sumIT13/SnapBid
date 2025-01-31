import json
from channels.generic.websocket import WebsocketConsumer, AsyncJsonWebsocketConsumer
from asgiref.sync import async_to_sync
from product.models import Product, Auction, Notification
import asyncio
from asgiref.sync import sync_to_async
from django.utils.timezone import now
from datetime import timedelta
import time


class BidConsumer(WebsocketConsumer):
    def connect(self):

        self.room_group_name = "bid_price"
        
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        auction_id = text_data_json["auction"]
        print(f"New Bid: {message} for Auction ID: {auction_id}")

        try:
            auction = Auction.objects.get(id=auction_id)
            auction.current_bid = message
            auction.bidder = self.scope["user"] # Set the bidder to the current user
            auction.save()

            notification = Notification.objects.create(user=auction.bidder, message=f"New bid of {message} placed on {auction.product.name}")
            notification.save()
            
            notify_message = notification.message
            notify_user = notification.user.username

            print(f"Notification: {notify_message} from User: {notify_user}")

            # Send updated bid to all connected clients
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name, 
                {
                    "type": "update_bid", 
                    "new_bid": message,
                    "auction_id": auction_id,
                    "notification": notify_message
                },
            )
        except Auction.DoesNotExist:
            print("Auction does not exist")

    def update_bid(self, event):
        new_bid = event["new_bid"]
        auction_id = event["auction_id"]

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            "new_bid": new_bid,
            "auction_id": auction_id
        }))
    
    def send_notification(self, event):
        notification = event["notification"]
        print(f"Sending Notification: {notification}")
        self.send(text_data=json.dumps({
            "notification": notification
        }))
 

class TimerStatusConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        """Handles WebSocket connection."""
        self.room_group_name = "timer_status"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        """Handles WebSocket disconnection."""
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """Handles incoming WebSocket messages and starts a countdown."""
        try:
            data = json.loads(text_data)
            auction_id = data.get("auction")
            
            if not auction_id:
                await self.send_json({"error": "Auction ID is required"})
                return

            # Fetch auction asynchronously
            auction = await self.get_auction(auction_id)
            if not auction:
                await self.send_json({"error": "Auction does not exist"})
                return

            # Start the countdown timer as a background task
            asyncio.create_task(self.start_timer(auction.end_time.timestamp(), auction_id))
        except json.JSONDecodeError:
            await self.send_json({"error": "Invalid JSON format"})

    async def start_timer(self, end_time, auction_id):
        """Runs a countdown timer in the background."""
        notification_sent = False

        while True:
            remaining_seconds = int(end_time - time.time())

            if remaining_seconds <= 300 and not notification_sent:  # 5-minute warning
                notification_sent = True
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "send_notification",
                        "message": "Auction Ending in 5 minutes",
                        "auction": auction_id
                    }
                )

            if remaining_seconds <= 0:
                await self.close_auction(auction_id)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "timer_update",
                        "message": "Auction Ended",
                        "auction": auction_id
                    }
                )
                break  # Stop the loop when time is up

            # Format remaining time as {X days, Y hrs, Z min, W sec}
            formatted_time = self.format_time(remaining_seconds)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "timer_update",
                    "message": formatted_time,
                    "auction": auction_id
                }
            )
            await asyncio.sleep(1)  # Update every second

    @staticmethod
    def format_time(seconds):
        """Converts seconds into days, hours, minutes, and seconds format."""
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{days} days, {hours} hrs, {minutes} min, {secs} sec"

    async def timer_update(self, event):
        """Handles sending timer updates to clients."""
        await self.send_json({
            "message": event["message"],
            "auction": event["auction"]
        })

    @sync_to_async
    def get_auction(self, auction_id):
        """Fetch auction object asynchronously."""
        return Auction.objects.filter(id=auction_id).first()

    @sync_to_async
    def close_auction(self, auction_id):
        """Closes the auction and updates the status."""
        auction = Auction.objects.filter(id=auction_id).first()
        if auction:
            auction.status = "Closed"
            auction.save()

            if auction.bidder:
                notify = Notification.objects.create(
                    user=auction.bidder,
                    message=f"Congratulations! You won the auction for {auction.product.name}."
                )
                async_to_sync(self.channel_layer.group_send)(
                self.room_group_name, 
                {
                    "type": "send_notification", 
                    "auction_id": auction_id,
                    "message": notify.message
                },
            )

    async def send_notification(self, event):
        """Sends auction notifications to clients."""
        print(f"Sending Notification: {event['message']}")
        await self.send_json({"notification": event["message"]})
