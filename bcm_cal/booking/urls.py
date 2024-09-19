from django.urls import path
from . import views

urlpatterns = [
    path("available_slots/", views.available_slots_week, name="available_slots_week"),
    path("book_slot/", views.book_slot, name="book_slot"),
    path("cancel_bookin/", views.cancel_booking, name="cancel_booking"),
    path("my_bookings/", views.my_bookings, name="my_bookings"),
    path("my_projects/", views.my_projects, name="my_projects"),
    path("project/<int:id>/", views.project_detail, name="project_detail"),
    path(
        "cancel_booking/<int:booking_id>/", views.cancel_booking, name="cancel_booking"
    ),
    path(
        "available_slots_week/<int:project_number>/",
        views.available_slots_week,
        name="available_slots_week",
    ),
    path("book_slot/", views.book_slot, name="book_slot"),
    path("book_slots/", views.book_slots, name="book_slots"),
    path(
        "available_slots_week/<int:project_number>/",
        views.available_slots_week,
        name="available_slots_week",
    ),
    path("create_project/", views.create_project, name="create_project"),
]
