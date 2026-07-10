"""Reviews admin."""
from django.contrib import admin
from .models import Complaint, Review, ReviewReply


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'reviewer', 'reviewee', 'rating', 'status', 'created_at']
    list_filter = ['status', 'rating']
    search_fields = ['reviewer__email', 'reviewee__email']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(ReviewReply)
class ReviewReplyAdmin(admin.ModelAdmin):
    list_display = ['id', 'review', 'author', 'created_at']
    readonly_fields = ['id', 'created_at']


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ['id', 'filed_by', 'subject', 'status', 'priority', 'created_at']
    list_filter = ['status', 'priority']
    search_fields = ['filed_by__email', 'subject']
    readonly_fields = ['id', 'created_at', 'updated_at']
