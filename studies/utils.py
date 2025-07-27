from datetime import datetime, timedelta, time
from collections import defaultdict
from .models import Task, Course
from django.utils import timezone



def time_range(start, end):
  """ List of hour ints between two time objects."""
  base = datetime.today().date()
  start_dt = datetime.combine(base, start)
  end_dt = datetime.combine(base, end)

  hours = []
  current = start_dt
  while current < end_dt:
    if current.hour not in hours:
      hours.append(current.hour)
    current += timedelta(hours=1)
  return hours

def get_availability(user, daily_start=10, daily_end=21):
  tasks = Task.objects.filter(owner=user, due_date__isnull=False)
  courses = Course.objects.filter(owner=user)
  today = timezone.now().date()

  if not tasks.exists():
    return {}
  
  latest_due = tasks.order_by('-due_date').first().due_date.date()
  availability = {}

  for n in range((latest_due - today).days + 1):
    current_day = today + timedelta(days=n)
    weekday_index = current_day.weekday()
    blocked_hours = []

    for course in courses:
      if (course.start_date is not None and course.start_date <= current_day) and \
        (course.end_date is not None and course.end_date >= current_day) and \
        weekday_index in course.days_of_week:
        blocked_hours.extend(
          time_range(course.start_time, course.end_time)
        )
    
    available_hours = [h for h in range(daily_start, daily_end) if h not in blocked_hours]
    availability[current_day.strftime('%Y-%m-%d')] = available_hours


  return availability