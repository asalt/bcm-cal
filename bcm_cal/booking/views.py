import calendar

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime, timedelta, time, date

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from .models import Booking
from .forms import BookingForm


@login_required
def available_slots_week(request):
    week_offset = int(request.GET.get("week_offset", 0))
    selected_date_str = request.GET.get("date", None)
    if selected_date_str:
        selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
    else:
        selected_date = date.today()
    print(selected_date)
    selected_date += timedelta(weeks=week_offset)
    print(selected_date)

    # Calculate the start and end dates of the week (Monday to Friday)
    start_of_week = selected_date - timedelta(days=selected_date.weekday())  # Monday
    end_of_week = start_of_week + timedelta(days=4)  # Friday
    start_of_month = date(selected_date.year, selected_date.month, 1)

    # Define time slots (e.g., every hour from 9 AM to 5 PM)
    time_slots = [time(hour) for hour in range(9, 17)]
    # time_slots = [time(hour).strftime('%H:%M:%S') for hour in range(9, 17)]

    # Prepare a dictionary to hold available slots for each day
    week_slots = dict()

    for day in range(5):
        current_date = start_of_week + timedelta(days=day)
        # Get booked slots for the current date
        booked_slots = Booking.objects.filter(date=current_date).values_list(
            "time_slot", flat=True
        )
        print(f"Date: {current_date}, Booked Slots: {list(booked_slots)}")
        # Determine available slots
        available_slots = [slot for slot in time_slots if slot not in booked_slots]
        print(f"Available Slots on {current_date}: {available_slots}")
        week_slots[current_date] = available_slots

    cal = calendar.Calendar(firstweekday=0)  # 0 = Monday
    month_days = cal.monthdatescalendar(selected_date.year, selected_date.month)
    month_days = [week[:5] for week in month_days]

    day_names = [
        "Mon",
        "Tue",
        "Wed",
        "Thu",
        "Fri",
    ]  # 'Sat', 'Sun']
    prev_week_date = start_of_week - timedelta(weeks=1)
    next_week_date = start_of_week + timedelta(weeks=1)

    # Calculate previous month date
    if selected_date.month == 1:
        prev_month_date = date(selected_date.year - 1, 12, 1) + timedelta(
            weeks=week_offset
        )
    else:
        prev_month_date = date(
            selected_date.year, selected_date.month - 1, 1
        ) + timedelta(weeks=week_offset)

    # Calculate next month date
    if selected_date.month == 12:
        next_month_date = date(selected_date.year + 1, 1, 1) + timedelta(
            weeks=week_offset
        )
    else:
        next_month_date = date(
            selected_date.year, selected_date.month + 1, 1
        ) + timedelta(weeks=week_offset)
    # still buggy with the highlighting after selection of new week.

    context = {
        "week_slots": week_slots,
        "start_of_week": start_of_week,
        "end_of_week": end_of_week,
        "time_slots": time_slots,
        "week_offset": week_offset,
        "form": BookingForm(),
        "today": date.today(),
        "month_days": month_days,  # Pass month calendar data to the template
        "selected_date": selected_date,  # Pass selected date to highlight the week
        "day_names": day_names,
        "prev_week_date": prev_week_date,
        "next_week_date": next_week_date,
        "prev_month_date": prev_month_date,
        "next_month_date": next_month_date,
    }

    return render(request, "booking/available_slots_week.html", context)


@login_required
def book_slot(request):
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            booking_date = form.cleaned_data["date"]
            booking_time = form.cleaned_data["time_slot"]
            # Proceed with booking logic...
            # Check for existing bookings, create a new booking, etc.
            # ...
            if Booking.objects.filter(
                date=booking_date, time_slot=booking_time
            ).exists():
                messages.error(request, "This time slot is already booked.")
                return redirect("available_slots")

            # Create the booking
            Booking.objects.create(
                user=request.user, date=booking_date, time_slot=booking_time
            )
            messages.success(request, "Your booking was successful.")
            return redirect("my_bookings")
        else:
            messages.error(request, "Invalid data submitted.")
            return redirect("available_slots")
    else:
        return redirect("available_slots")


@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by("date", "time_slot")
    context = {"bookings": bookings}
    return render(request, "booking/my_bookings.html", context)


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the user in after signup
            login(request, user)
            return redirect("available_slots")
    else:
        form = UserCreationForm()
    return render(request, "registration/signup.html", {"form": form})


@login_required
def cancel_booking(request, booking_id):
    booking = Booking.objects.get(id=booking_id, user=request.user)
    if request.method == "POST":
        booking.delete()
        messages.success(request, "Your booking has been canceled.")
        return redirect("my_bookings")
    return render(request, "booking/cancel_booking.html", {"booking": booking})
