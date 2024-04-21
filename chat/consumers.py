import json

from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from chat.models import Users, Room, Message


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )

        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )

    # Receive a message from WebSocket
    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)

        await self.save_messages(data)

        # Send a message to a room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat.message',
                'data': data
            }
        )

    # receive a message from room group
    async def chat_message(self, event):
        room = event['data']['room']
        message = event['data']['message']
        user = self.scope['user']

        await self.send(
            text_data=json.dumps({
                'room': room,
                'message': message,
                'username': user.get_full_name()
            })
        )

    @sync_to_async
    def save_messages(self, data):
        user_email = self.scope['user'].email
        user = Users.objects.get(email=user_email)
        room = Room.objects.get(slug=data['room'])
        Message.objects.create(user=user, room=room, content=data['message'])
