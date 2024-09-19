from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from .models import Booking, Availability


class AvailabilityInline(admin.TabularInline):
    model = Availability
    extra = 1


class BookingForm(ModelForm):
    class Meta:
        model = Booking
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get("date")
        time_slot = cleaned_data.get("time_slot")

        if Booking.objects.filter(date=date, time_slot=time_slot).exists():
            raise ValidationError("This time slot is already booked.")


class BookingAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "time_slot")
    inlines = [AvailabilityInline]


class BookingAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "time_slot", "booking_count")
    # list_display = ("user", "date", "time_slot")
    list_filter = ("date", "time_slot")
    search_fields = ("user__username",)

    def booking_count(self, obj):
        return Booking.objects.filter(date=obj.date).count()

    booking_count.short_description = "Total Bookings for Date"


admin.site.register(Booking, BookingAdmin)
