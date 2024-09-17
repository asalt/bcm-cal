from django.contrib import admin
from .models import Booking


class BookingAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "time_slot")
    list_filter = ("date", "time_slot")
    search_fields = ("user__username",)


admin.site.register(Booking, BookingAdmin)
