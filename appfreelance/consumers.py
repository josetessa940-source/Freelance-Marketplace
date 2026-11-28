from django.db import models
import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Contract, Message


class ChatConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.contract_id = self.scope['url_route']['kwargs']['contract_id']
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            await self.close()
            return

        if not await self.check_permission():
            await self.close()
            return

        self.room_group_name = f'chat_{self.contract_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name)

        await self.accept()

        messages = await self.get_chat_history()

        await self.send_json({
            'type': 'history',
            'messages': messages})

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name,self.channel_name)

    async def receive_json(self, content):
        print("CONNECTED USER:", self.user.username)
        message = content.get('message', '').strip()

        if not message or len(message) > 2000:
            return

        saved_message = await self.save_message(message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {'type': 'chat_message','message': saved_message})

    async def chat_message(self, event):
        await self.send_json(event['message'])

    @database_sync_to_async
    def check_permission(self):
        return Contract.objects.filter(
            id=self.contract_id
        ).filter(
            models.Q(proposal__project__client=self.user) |
            models.Q(proposal__freelancer=self.user)
        ).exists()

    @database_sync_to_async
    def save_message(self, message):
        obj = Message.objects.create(
            contract_id=self.contract_id,
            sender=self.user,
            content=message)

        return {
            'sender': self.user.username,
            'message': obj.content,
            'timestamp': obj.timestamp.isoformat(),
            'is_read': obj.is_read}

    @database_sync_to_async
    def get_chat_history(self):
        messages = Message.objects.filter(
            contract_id=self.contract_id
        ).select_related('sender').order_by('timestamp')

        return [
            {
                'sender': msg.sender.username,
                'message': msg.content,
                'timestamp': msg.timestamp.isoformat(),
                'is_read': msg.is_read
            }
            for msg in messages]