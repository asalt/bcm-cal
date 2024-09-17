from django.urls import path
from . import views

urlpatterns = [
    path('available_slots/', views.available_slots_week, name='available_slots_week'),
    path('book_slot/', views.book_slot, name='book_slot'),
    path('my_bookings/', views.my_bookings, name='my_bookings'),
    path('cancel_booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),

]

