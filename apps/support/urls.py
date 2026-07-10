"""URL configuration for Support module."""
from django.urls import path
from .views import ChatbotView, FAQListView, TicketDetailView, TicketListView, AdminTicketListView, AdminTicketDetailView

app_name = 'support'

urlpatterns = [
    path('tickets/', TicketListView.as_view(), name='ticket-list'),
    path('tickets/<uuid:ticket_id>/', TicketDetailView.as_view(), name='ticket-detail'),
    path('faqs/', FAQListView.as_view(), name='faq-list'),
    path('chatbot/', ChatbotView.as_view(), name='chatbot'),
    path('admin/tickets/', AdminTicketListView.as_view(), name='admin-ticket-list'),
    path('admin/tickets/<uuid:ticket_id>/', AdminTicketDetailView.as_view(), name='admin-ticket-detail'),
]
