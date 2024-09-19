import calendar

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime, timedelta, time, date

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from .models import Booking, Project
from .forms import BookingForm, ProjectForm
from .utils import get_week_dates, get_time_slots, get_week_slots


def get_project_number():
    for i in range(1, 10000):
        if not Project.objects.filter(project_number=i).exists():
            yield i


project_number_generator = (
    get_project_number()
)  # tempory here, in practice will be moved out to separ


@login_required
def create_project(request):

    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project_number = next(project_number_generator)
            project.save()
            messages.success(request, "Project created successfully.")
            return redirect("select_time_slots", project_number=project.project_number)
    else:
        form = ProjectForm()
    return render(request, "booking/create_project.html", {"form": form})


@login_required
def book_slot(request):
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            booking_date = form.cleaned_data["date"]
            booking_time = form.cleaned_data["time_slot"]
            project_number = form.cleaned_data["project_number"]

            # Retrieve the project
            project = get_object_or_404(
                Project, project_number=project_number, user=request.user
            )

            # Check if the slot is already booked
            if Booking.objects.filter(
                date=booking_date, time_slot=booking_time
            ).exists():
                messages.error(request, "This time slot is already booked.")
                return redirect("available_slots_week", project_number=project_number)

            # Create the booking
            Booking.objects.create(
                user=request.user,
                project=project,
                date=booking_date,
                time_slot=booking_time,
            )
            messages.success(request, "Your booking was successful.")
            return redirect("my_bookings")
        else:
            messages.error(request, "Invalid data submitted.")
            project_number = request.POST.get("project_number")
            return redirect("available_slots_week", project_number=project_number)
    else:
        messages.error(request, "Invalid request method.")
        project_number = request.POST.get("project_number", "")
        return redirect("available_slots_week", project_number=project_number)


@login_required
def book_slots(request):
    if request.method == "POST":
        project_number = request.POST.get("project_number")
        selected_slots = request.POST.getlist(
            "selected_slots"
        )  # List of "YYYY-MM-DD,HH:MM:SS" strings

        project = get_object_or_404(
            Project, project_number=project_number, user=request.user
        )
        bookings_created = 0

        for slot in selected_slots:
            date_str, time_str = slot.split(",")
            booking_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            booking_time = datetime.strptime(time_str, "%H:%M:%S").time()

            # Check if the slot is already booked
            if not Booking.objects.filter(
                date=booking_date, time_slot=booking_time
            ).exists():
                Booking.objects.create(
                    user=request.user,
                    project=project,
                    date=booking_date,
                    time_slot=booking_time,
                )
                bookings_created += 1

                if bookings_created >= 3:
                    break  # Limit to 3 bookings per project

        if bookings_created > 0:
            messages.success(request, f"{bookings_created} booking(s) created.")
        else:
            messages.error(
                request,
                "No bookings were created. The selected slots may already be booked.",
            )

        return redirect("my_bookings")
    else:
        messages.error(request, "Invalid request method.")
        project_number = request.POST.get("project_number", "")
        return redirect("available_slots_week", project_number=project_number)


@login_required
def available_slots_week(request, project_number=None):

    # Retrieve user's projects
    projects = Project.objects.filter(user=request.user)

    # Get selected project number from GET parameters
    project_number = request.GET.get("project_number")

    # If project_number is provided, get the project
    if project_number:
        try:
            project_number = int(project_number)
            project = Project.objects.get(
                project_number=project_number, user=request.user
            )
        except (ValueError, Project.DoesNotExist):
            project = None
    else:
        project = None

    week_offset = int(request.GET.get("week_offset", 0))
    selected_date_str = request.GET.get("date", None)

    # Determine the selected date
    if selected_date_str:
        selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
    else:
        selected_date = date.today()

    # Ensure the selected date is not in the past
    today = date.today()
    if selected_date < today:
        selected_date = today

    # Apply week offset
    selected_date += timedelta(weeks=week_offset)

    # Use helper function to get start and end dates of the week
    start_of_week, end_of_week = get_week_dates(selected_date)

    # Get time slots
    time_slots = get_time_slots()

    # Get week slots
    week_slots = get_week_slots(start_of_week, time_slots)

    # Generate month calendar data
    cal = calendar.Calendar(firstweekday=0)  # 0 = Monday
    month_days = cal.monthdatescalendar(selected_date.year, selected_date.month)
    month_days = [week[:5] for week in month_days]

    # For highlighting purposes, we need to know the days in the current week
    week_days = [
        start_of_week + timedelta(days=i) for i in range(5)
    ]  # Monday to Friday

    # Prepare day names (Monday to Friday)
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri"]

    # Calculate previous and next week dates
    prev_week_date = start_of_week - timedelta(weeks=1)
    next_week_date = start_of_week + timedelta(weeks=1)

    # Calculate previous and next month dates
    if selected_date.month == 1:
        prev_month_date = date(selected_date.year - 1, 12, 1)
    else:
        prev_month_date = date(selected_date.year, selected_date.month - 1, 1)

    if selected_date.month == 12:
        next_month_date = date(selected_date.year + 1, 1, 1)
    else:
        next_month_date = date(selected_date.year, selected_date.month + 1, 1)

    slot_data = []
    for slot in time_slots:
        row = {"time": slot, "days": []}
        for day in week_days:
            # Determine status and class names
            day_info = {
                "date": day,
                "status": "available",  # or 'booked', 'not_available'
                "class": "btn-success",  # or 'text-muted', etc.
                "can_book": True,  # or False
            }
            row["days"].append(day_info)
        slot_data.append(row)

    context = {
        "week_slots": week_slots,
        "start_of_week": start_of_week,
        "end_of_week": end_of_week,
        "time_slots": time_slots,
        "week_offset": week_offset,
        "form": BookingForm(),
        "today": today,
        "month_days": month_days,  # Pass month calendar data to the template
        "selected_date": selected_date,  # Pass selected date to highlight the week
        "day_names": day_names,
        "prev_week_date": prev_week_date,
        "next_week_date": next_week_date,
        "prev_month_date": prev_month_date,
        "next_month_date": next_month_date,
        "week_days": week_days,  # Pass week days for highlighting
        "project_number": project_number,
        "projects": projects,
        "project": project,  # selected project
    }

    return render(request, "booking/available_slots_week.html", context)


@login_required
def available_slots_week(request):
    # Get week_offset from GET parameters; default is 0
    week_offset = int(request.GET.get("week_offset", 0))

    # Get the selected_date from GET parameters; default is today
    selected_date_str = request.GET.get("date", None)
    if selected_date_str:
        try:
            selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
        except ValueError:
            selected_date = date.today()
    else:
        selected_date = date.today()

    # Apply week_offset
    selected_date += timedelta(weeks=week_offset)

    # Ensure selected_date is not in the past
    today = date.today()
    if selected_date < today:
        selected_date = today

    # Get start and end of the week using helper function
    start_of_week, end_of_week = get_week_dates(selected_date)

    # Get time slots using helper function
    time_slots = get_time_slots()

    # Get available slots for the week using helper function
    week_slots = get_week_slots(start_of_week, time_slots)

    # Prepare month calendar data
    cal = calendar.Calendar(firstweekday=0)  # 0 = Monday
    month_days = cal.monthdatescalendar(selected_date.year, selected_date.month)
    month_days = [week[:5] for week in month_days]  # Monday to Friday

    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri"]

    # Calculate previous and next week dates
    prev_week_date = start_of_week - timedelta(weeks=1)
    next_week_date = start_of_week + timedelta(weeks=1)

    # Calculate previous and next month dates
    if selected_date.month == 1:
        prev_month_date = date(selected_date.year - 1, 12, 1)
    else:
        prev_month_date = date(selected_date.year, selected_date.month - 1, 1)

    if selected_date.month == 12:
        next_month_date = date(selected_date.year + 1, 1, 1)
    else:
        next_month_date = date(selected_date.year, selected_date.month + 1, 1)

    # Format time_slots for the template
    formatted_time_slots = [slot["time"] for slot in week_slots]
    # Note: 'week_slots' now contains 'time' and 'days'

    context = {
        "week_slots": week_slots,  # List of slot dictionaries
        "start_of_week": start_of_week,
        "end_of_week": end_of_week,
        "time_slots": [slot["time"] for slot in week_slots],  # List of time strings
        "week_offset": week_offset,
        "form": BookingForm(),
        "today": today,
        "month_days": month_days,
        "selected_date": selected_date,
        "day_names": day_names,
        "prev_week_date": prev_week_date,
        "next_week_date": next_week_date,
        "prev_month_date": prev_month_date,
        "next_month_date": next_month_date,
    }

    return render(request, "booking/available_slots_week.html", context)


@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by("date", "time_slot")
    context = {"bookings": bookings}
    return render(request, "booking/my_bookings.html", context)


@login_required
def my_projects(request):
    projects = Project.objects.filter(user=request.user)
    context = {"projects": projects}
    return render(request, "booking/my_projects.html", context)


@login_required
def project_detail(request, id):
    project = get_object_or_404(Project, id=id, user=request.user)
    context = {"project": project}
    return render(request, "booking/project_detail.html", context)


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
def cancel_booking(request):
    if request.method == "POST":
        booking_id = request.POST.get("booking_id")
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
        booking.delete()
        messages.success(request, "Booking canceled successfully.")
    else:
        messages.error(request, "Invalid request method.")
    return redirect("my_bookings")
