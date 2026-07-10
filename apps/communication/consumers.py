"""Communication WebSocket consumer — real-time chat."""
import json
import logging

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser

from . import constants

logger = logging.getLogger('carebridge')


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time chat.

    URL: ws://host/ws/chat/<conversation_id>/

    On connect:
      - Authenticate via JWT (AuthMiddlewareStack).
      - Verify user is a participant of the conversation.
      - Join the conversation's channel group.
      - Mark messages as delivered.

    On receive:
      - Handle typing indicators directly over WS (low-latency).
      - Message sending is done via REST; WS is receive-only for messages.

    On disconnect:
      - Leave the channel group.
    """

    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.group_name = f"{constants.CHAT_GROUP_PREFIX}{self.conversation_id}"
        self.user = self.scope.get('user')

        if not self.user or isinstance(self.user, AnonymousUser) or not self.user.is_authenticated:
            await self.close(code=4001)
            return

        if not await self._is_participant():
            await self.close(code=4003)
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # Mark messages as delivered on connect
        await self._mark_delivered()
        logger.info("WS CONNECT user=%s conversation=%s", self.user.id, self.conversation_id)

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
        logger.info("WS DISCONNECT user=%s conversation=%s", getattr(self, 'user', '?'), self.conversation_id)

    async def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self._send_error('Invalid JSON.')
            return

        msg_type = data.get('type')
        if msg_type in (constants.WS_TYPE_TYPING, constants.WS_TYPE_STOP_TYPING):
            await self._handle_typing(msg_type)
        else:
            await self._send_error(f'Unsupported WS message type: {msg_type}')

    async def chat_message(self, event):
        """Relay group messages to the WebSocket client."""
        await self.send(text_data=json.dumps({
            'type': event['message_type'],
            'payload': event['payload'],
        }))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @database_sync_to_async
    def _is_participant(self) -> bool:
        from .repositories import ParticipantRepository
        return ParticipantRepository.is_participant(self.conversation_id, self.user.id)

    @database_sync_to_async
    def _mark_delivered(self):
        from .repositories import MessageRepository
        MessageRepository.mark_delivered(self.conversation_id, exclude_sender_id=self.user.id)

    async def _handle_typing(self, msg_type: str):
        from django.utils import timezone
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'chat.message',
                'message_type': msg_type,
                'payload': {
                    'conversation_id': self.conversation_id,
                    'user_id': str(self.user.id),
                    'user_name': self.user.get_full_name(),
                },
            },
        )

    async def _send_error(self, message: str):
        await self.send(text_data=json.dumps({
            'type': constants.WS_TYPE_ERROR,
            'payload': {'message': message},
        }))
