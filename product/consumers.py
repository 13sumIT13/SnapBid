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


active_timers: dict[int, asyncio.Task] = {}


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
    
# consumers.py
class TimerStatusConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.auction_id = self.scope["url_route"]["kwargs"]["auction_id"]
        self.room_group_name = f"auction_{self.auction_id}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        auction = await sync_to_async(Auction.objects.get)(id=self.auction_id)
        end_time_ts = auction.end_time.timestamp()

        # Send end_time once on connect
        await self.send_json({
            "type": "end_time",
            "end_time": end_time_ts,
        })

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
