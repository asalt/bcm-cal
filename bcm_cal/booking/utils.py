# booking/utils.py
from collections import defaultdict
from datetime import date, timedelta, time, date
from .models import Booking


def get_week_dates(selected_date):
    """
    Given a selected_date, returns the start and end dates of the week (Monday to Friday).
    """
    start_of_week = selected_date - timedelta(days=selected_date.weekday())  # Monday
    end_of_week = start_of_week + timedelta(days=4)  # Friday
    return start_of_week, end_of_week


def get_time_slots(hr_min=9, hr_max=17):
    """
    Returns a list of time slots from (default) 9 AM to 5 PM.
    """
    return [time(hour) for hour in range(hr_min, hr_max)]


def get_week_slots(start_of_week, time_slots):
    """
    For each time slot, determine its status for each day in the week.
    Returns a list of dictionaries, each representing a time slot and its status across the week.
    """
    week_slots = []
    end_of_week = start_of_week + timedelta(days=4)  # Friday

    # Fetch all bookings for the week in a single query
    bookings = Booking.objects.filter(date__range=(start_of_week, end_of_week))

    # Organize bookings by date for quick lookup
    bookings_by_date = defaultdict(set)
    for booking in bookings:
        bookings_by_date[booking.date].add(booking.time_slot)

    # Iterate through each time slot
    for slot in time_slots:
        slot_time_str = slot.strftime("%H:%M")
        slot_entry = {"time": slot_time_str, "days": []}

        # Iterate through each day of the week
        for day_offset in range(5):  # Monday to Friday
            current_date = start_of_week + timedelta(days=day_offset)
            booked_slots = bookings_by_date.get(current_date, set())
            the_day = start_of_week + timedelta(days=day_offset)
            if the_day < date.today():
                slot_info = {
                    "status": "not_available",
                    "class": "text-secondary",  # For past slots
                }
            elif slot in booked_slots:
                slot_info = {
                    "status": "booked",
                    "class": "text-danger",  # For booked slots
                }
            else:
                slot_info = {
                    "status": "available",
                    "class": "text-success",  # For available slots
                }

            slot_entry["days"].append(
                {
                    "date": current_date,
                    "status": slot_info["status"],
                    "class": slot_info["class"],
                }
            )

        week_slots.append(slot_entry)

    return week_slots
