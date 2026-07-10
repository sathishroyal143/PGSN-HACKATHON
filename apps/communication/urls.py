"""Communication URL configuration."""
from django.urls import path
from .views import (
    CallAnswerView, CallDeclineView, CallEndView, CallListView,
    ConversationDetailView, ConversationListView,
    CreateDirectConversationView, MarkReadView,
    MessageDeleteView, MessageListView, TypingView,
)

app_name = 'communication'

urlpatterns = [
    # Conversations
    path('conversations/', ConversationListView.as_view(), name='conversation-list'),
    path('conversations/direct/', CreateDirectConversationView.as_view(), name='conversation-direct'),
    path('conversations/<uuid:conversation_id>/', ConversationDetailView.as_view(), name='conversation-detail'),

    # Messages
    path('conversations/<uuid:conversation_id>/messages/', MessageListView.as_view(), name='message-list'),
    path('conversations/<uuid:conversation_id>/messages/<uuid:message_id>/', MessageDeleteView.as_view(), name='message-delete'),
    path('conversations/<uuid:conversation_id>/read/', MarkReadView.as_view(), name='mark-read'),
    path('conversations/<uuid:conversation_id>/typing/', TypingView.as_view(), name='typing'),

    # Calls
    path('conversations/<uuid:conversation_id>/calls/', CallListView.as_view(), name='call-list'),
    path('conversations/<uuid:conversation_id>/calls/<uuid:call_id>/answer/', CallAnswerView.as_view(), name='call-answer'),
    path('conversations/<uuid:conversation_id>/calls/<uuid:call_id>/decline/', CallDeclineView.as_view(), name='call-decline'),
    path('conversations/<uuid:conversation_id>/calls/<uuid:call_id>/end/', CallEndView.as_view(), name='call-end'),
]
