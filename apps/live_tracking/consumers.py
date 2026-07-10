"""Live Tracking WebSocket consumer."""
import json
import logging

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser

from apps.bookings.models import Booking
from . import constants

logger = logging.getLogger('carebridge')


class TrackingConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for live tracking.

    URL: ws://host/ws/tracking/<booking_id>/

    On connect:
      - Authenticate via JWT (handled by AuthMiddlewareStack).
      - Verify the user is a participant of the booking.
      - Join the booking's channel group.

    On receive:
      - Companions can push location updates directly over WS
        (alternative to the REST endpoint for lower latency).

    On disconnect:
      - Leave the channel group.
    """

    async def connect(self):
        self.booking_id = self.scope['url_route']['kwargs']['booking_id']
        self.group_name = f"{constants.TRACKING_GROUP_PREFIX}{self.booking_id}"
        self.user = self.scope.get('user')

        if not self.user or isinstance(self.user, AnonymousUser) or not self.user.is_authenticated:
            await self.close(code=4001)
            return

        authorized = await self._is_participant()
        if not authorized:
            await self.close(code=4003)
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        logger.info("WS CONNECT user=%s booking=%s", self.user.id, self.booking_id)

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
        logger.info("WS DISCONNECT user=%s booking=%s code=%s", getattr(self, 'user', '?'), self.booking_id, close_code)

    async def receive(self, text_data=None, bytes_data=None):
        """
        Companions may send location pings directly over WebSocket.
        Message format: {"type": "location_update", "latitude": ..., "longitude": ..., ...}
        """
        if not text_data:
            return
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self._send_error('Invalid JSON.')
            return

        msg_type = data.get('type')
        if msg_type == constants.WS_TYPE_LOCATION_UPDATE:
            await self._handle_location_update(data)
        else:
            await self._send_error(f'Unknown message type: {msg_type}')

    async def tracking_message(self, event):
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
        from apps.users.models import UserRole
        if self.user.role in (UserRole.ADMIN, UserRole.SUPPORT):
            return True
        booking = Booking.objects.filter(id=self.booking_id, is_deleted=False).first()
        if not booking:
            return False
        return self.user.id in (booking.family_user_id, booking.companion_id)

    @database_sync_to_async
    def _persist_location(self, data: dict):
        from django.utils import timezone
        from apps.bookings.models import Booking
        from .services import LocationService

        booking = Booking.objects.filter(id=self.booking_id, is_deleted=False).first()
        if not booking:
            return None

        payload = {
            'latitude': data.get('latitude'),
            'longitude': data.get('longitude'),
            'accuracy': data.get('accuracy'),
            'speed': data.get('speed'),
            'heading': data.get('heading'),
            'altitude': data.get('altitude'),
            'source': constants.SOURCE_COMPANION_APP,
            'recorded_at': data.get('recorded_at', timezone.now().isoformat()),
        }
        try:
            return LocationService.record_location(booking, self.user, payload)
        except Exception as exc:
            logger.warning("WS location persist failed: %s", exc)
            return None

    async def _handle_location_update(self, data: dict):
        update = await self._persist_location(data)
        if not update:
            await self._send_error('Could not record location.')

    async def _send_error(self, message: str):
        await self.send(text_data=json.dumps({
            'type': constants.WS_TYPE_ERROR,
            'payload': {'message': message},
        }))
