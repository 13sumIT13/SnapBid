import json

from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from product.models import Product, Auction

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