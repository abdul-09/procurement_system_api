import json
from asgiref.sync import async_to_sync, sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Notification

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_authenticated:
            self.group_name = f'Notifications_{self.user.id}'
            await self.accept()
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            print(f"User {self.user.id} connected to group {self.group_name} on channel {self.channel_name}")

            #Fetch undelivered notifications asynchronously
            undelivered_notifications = await sync_to_async(list)(
                Notification.objects.filter(user=self.user, delivered=False)
            )

            # Send undelivered notifications
            for notification in undelivered_notifications:
                await self.send_notification({
                    'message': notification.message
                })
                # Mark as delivered and sent after sending the notification
                notification.delivered = True
                await sync_to_async(notification.save)()
            
    async def disconnect(self, close_code):
        if self.user.is_authenticated:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            print(f"User {self.user.id} disconnected from group {self.group_name} on channel {self.channel_name}")

    async def receive(self, text_data):
        pass

    async def send_notification(self, event):
        print(f"Sending notification to user {self.user.id} on channel {self.channel_name}")
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))