"""Support admin."""
from django.contrib import admin
from .models import ChatbotLog, FAQ, Ticket, TicketMessage


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'subject', 'category', 'priority', 'status', 'created_at']
    list_filter = ['status', 'priority', 'category']
    search_fields = ['user__email', 'subject']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(TicketMessage)
class TicketMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'ticket', 'sender', 'is_staff_reply', 'created_at']
    list_filter = ['is_staff_reply']
    readonly_fields = ['id', 'created_at']


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['id', 'category', 'question', 'is_published', 'order']
    list_filter = ['category', 'is_published']
    search_fields = ['question']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(ChatbotLog)
class ChatbotLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'intent', 'created_at']
    list_filter = ['intent']
    readonly_fields = ['id', 'created_at']
