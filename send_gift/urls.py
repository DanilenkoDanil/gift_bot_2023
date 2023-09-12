from .views import SendGiftAPIView, ChangeLinkAPIView, CheckFriendAPIView
from django.urls import path

urlpatterns = [
    path('change-link', ChangeLinkAPIView.as_view(), name='change-link'),
    path('check-friend', CheckFriendAPIView.as_view(), name='check-friend'),
    path('get-gift', SendGiftAPIView.as_view(), name='get-gift'),
]
