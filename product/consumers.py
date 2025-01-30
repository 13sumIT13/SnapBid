import json
from channels.generic.websocket import WebsocketConsumer, AsyncJsonWebsocketConsumer
from asgiref.sync import async_to_sync
from product.models import Product, Auction
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
            auction.save()

            # Send updated bid to all connected clients
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name, 
                {
                    "type": "update_bid", 
                    "new_bid": message,
                    "auction_id": auction_id,
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
class TimerStatusConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        """Handles WebSocket connection"""
        self.room_group_name = "timer_status"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        """Handles WebSocket disconnection"""
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """Handles incoming WebSocket messages and starts a countdown."""
        text_data_json = json.loads(text_data)
        auction_id = text_data_json.get("auction")

        # Fetch auction asynchronously
        auction = await self.get_auction(auction_id)
        if not auction:
            await self.send_json({"error": "Auction does not exist"})
            return

        # Start the countdown timer as a background task
        asyncio.create_task(self.start_timer(auction.end_time.timestamp(), auction_id))

    async def start_timer(self, end_time, auction_id):
        """Runs a countdown timer in the background with {X days, Y hrs, Z min, W sec} format."""
        while True:
            remaining_seconds = int(end_time - time.time())

            if remaining_seconds <= 0:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "timer_update",
                        "message": "Auction Ended",
                        "auction": auction_id
                    }
                )
                break  # Stop the loop when time is up

            # Convert seconds to days, hours, minutes, and seconds
            days = remaining_seconds // 86400
            hours = (remaining_seconds % 86400) // 3600
            minutes = (remaining_seconds % 3600) // 60
            seconds = remaining_seconds % 60

            # Format the message in required format
            formatted_time = f"{days} days, {hours} hrs, {minutes} min, {seconds} sec"

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "timer_update",
                    "message": formatted_time,  # Send formatted time
                    "auction": auction_id
                }
            )
            await asyncio.sleep(1)  # Wait for 1 second before updating

    async def timer_update(self, event):
        """Handles sending timer updates to clients."""
        await self.send_json({
            "message": event["message"],  # Now it's in {X days, Y hrs, Z min, W sec} format
            "auction": event["auction"]
        })

    @sync_to_async
    def get_auction(self, auction_id):
        """Fetch auction object asynchronously."""
        try:
            return Auction.objects.get(id=auction_id)
        except Auction.DoesNotExist:
            return None