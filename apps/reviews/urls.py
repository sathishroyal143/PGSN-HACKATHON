"""URL configuration for Reviews module."""
from django.urls import path
from .views import ComplaintDetailView, ComplaintListView, RevieweeReviewsView, ReviewListView, ReviewReplyView

app_name = 'reviews'

urlpatterns = [
    path('', ReviewListView.as_view(), name='review-list'),
    path('user/<int:user_id>/', RevieweeReviewsView.as_view(), name='reviewee-reviews'),
    path('<uuid:review_id>/reply/', ReviewReplyView.as_view(), name='review-reply'),
    path('complaints/', ComplaintListView.as_view(), name='complaint-list'),
    path('complaints/<uuid:complaint_id>/', ComplaintDetailView.as_view(), name='complaint-detail'),
]
