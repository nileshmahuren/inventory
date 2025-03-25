from django.urls import path
from .views import book_item, cancel_booking

urlpatterns = [
    path('book/', book_item, name='book_item'),
    path('cancel/', cancel_booking, name='cancel_booking'),
]
