from datetime import datetime, timedelta, time
from collections import defaultdict
from .models import Task, Course, ScheduledTask
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
  now = timezone.localtime()
  today = now.date()

  if not tasks.exists():
    return {}
  
  latest_due = tasks.order_by('-due_date').first().due_date
  last_day = timezone.localtime(latest_due).date()

  availability = {}
  for day_offset in range((last_day - today).days + 1):
    day = today + timedelta(days=day_offset)
    # weekday_index = current_day.weekday()
    # blocked_hours = []

    # Start hour
    if day == today:
      start_hour = max(daily_start, now.hour + 1)
    else:
      start_hour = daily_start

    # Tasks due on this local day
    start_of_day = timezone.make_aware(datetime.combine(day, time.min))
    end_of_day = timezone.make_aware(datetime.combine(day, time.max))
    due_today = tasks.filter(
      due_date__gte=start_of_day,
      due_date__lte=end_of_day
    )
    
    if due_today.exists():
      due_hours = []
      for t in due_today:
        due_local = timezone.localtime(t.due_date)
        due_hours.append(due_local.hour + (1 if due_local.minute > 0 else 0))
      end_hour = min(daily_end, min(due_hours))
    else:
      end_hour = daily_end
    
    # block course hours
    blocked = []
    weekday = day.weekday()

    for c in courses:
      if c.start_date <= day <= c.end_date and weekday in c.days_of_week:
        blocked.extend(
          time_range(c.start_time, c.end_time)
        )
    
    # Block user-edited schedule hours 
    user_slots = ScheduledTask.objects.filter(
      task__owner = user,
      # assigned_by='user',
      start_datetime__gte=start_of_day,
      start_datetime__lte=end_of_day
    ).values_list('start_datetime', flat=True)

    print(f'user_slots {user_slots}')
    for dt in user_slots:
      blocked.append(timezone.localtime(dt).hour)
      
    blocked_set = set(blocked)
    available_hours = [h for h in range(start_hour, end_hour) if h not in blocked_set]
    availability[day.strftime('%Y-%m-%d')] = available_hours
    # availability[current_day] = available_hours

  return availability