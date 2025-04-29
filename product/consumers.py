import json
from channels.generic.websocket import WebsocketConsumer, AsyncJsonWebsocketConsumer
from asgiref.sync import async_to_sync
from product.models import Product, Auction, Bid
import asyncio
from asgiref.sync import sync_to_async
from django.utils.timezone import now
from datetime import timedelta
import time
from notification.models import Notification
from channels.layers import get_channel_layer
from django.utils import timezone


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

            # Store the current bidder before updating
            current_bidder = auction.bidder

            # Update the auction with the new bid
            auction.current_bid = message
            auction.bidder = self.scope["user"]  # Set the bidder to the current user
            auction.save()

            # Initialize variables for notification
            notify_message = None
            notify_user = None

            # Check if there was a previous bidder
            if current_bidder:  # If there was a previous bidder
                prev_bid = Bid.objects.filter(auction=auction, user=current_bidder).first()

                if prev_bid:
                    prev_bidder = prev_bid.user
                    notification = Notification.objects.create(
                        user=prev_bidder,
                        heading="Outbid Notification",
                        message=f"New bid of {message} placed on {auction.product.name} by {auction.bidder.username}. The current bid is {auction.current_bid}."
                    )
                    notification.save()
                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        f"user_{prev_bidder.id}",  
                        {
                            "type" : "send_notification",
                            "notification": {
                                "id": notification.id,
                                "message": notification.message,
                                "heading": notification.heading,
                            }
                        }
                    )

            # Create the new bid
            bid = Bid.objects.create(auction=auction, user=self.scope["user"], bid_amount=message)
            bid.save()

            # Send updated bid to all connected clients
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name, 
                {
                    "type": "update_bid",
                    "new_bid": message,
                    "auction_id": auction_id,
                    "bidder": auction.bidder.username if auction.bidder else None
                },
            )
        except Auction.DoesNotExist:
            print("Auction does not exist")

    def update_bid(self, event):
        new_bid = event["new_bid"]
        auction_id = event["auction_id"]
        bidder = event["bidder"]

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            "new_bid": new_bid,
            "auction_id": auction_id,
            "bidder": bidder,
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
                existing = await sync_to_async(
                Notification.objects.filter(
                        user=self.scope["user"],
                        heading="Auction Ending Soon",
                        created_at__gte=timezone.now() - timedelta(minutes=5)
                    ).exists
                )()

             
                if not existing:
                    notification = await sync_to_async(Notification.objects.create)(
                        user=self.scope["user"],
                        heading="Auction Ending Soon",
                        message=f"The auction for {auction_id} is ending in 5 minutes."
                    )
                    channel_layer = get_channel_layer()
                    await channel_layer.group_send(
                        f"user_{self.scope['user'].id}",  # Send to the user's group
                        {
                            "type" : "send_notification",
                            "notification": {
                                "id": notification.id,
                                "message": notification.message,
                                "heading": notification.heading,
                            }
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

        return {
            "days": days,
            "hours": hours,
            "minutes": minutes,
            "seconds": secs
        }

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
                notification = Notification.objects.create(
                    user=auction.bidder,
                    heading=f"Auction Won : {auction.product.name}",
                    message=f"You have won the auction for {auction.product.name}! Your bid of {auction.current_bid} was successful. Please proceed with the payment and complete your purchase."
                    
                )
                notification.save()
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f"user_{auction.bidder.id}",  # Send to the user's group
                    {
                        "type" : "send_notification",
                        "notification": {
                            "id": notification.id,
                            "message": notification.message,
                            "heading": notification.heading
                        }
                    }
                )
 