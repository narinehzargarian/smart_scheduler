from datetime import datetime, timedelta
from django.utils import timezone
# import pytz
from .utils import get_availability
from .algorithms import rule_based_scheduler
from .models import Task, ScheduledTask

# pt = pytz.timezone('America/Los_Angeles')

def generate_schedule(user):
  print('Generate schedule has been called!')
  availability = get_availability(user)
  # QuerySet of tasks
  tasks_qs = Task.objects.filter(owner=user, due_date__isnull=False)

  # Convert to list of dicts
  tasks = [{
    'name': t.name,
    'due_date': t.due_date.strftime('%Y-%m-%d %I:%M %p'),
    'estimated_duration' : int(t.estimated_duration.total_seconds() // 3600)
  } for t in tasks_qs]

  schedule = rule_based_scheduler(availibility=availability, tasks=tasks)

  # Delete the old auto schedule
  ScheduledTask.objects.filter(
    task__owner=user,
    assigned_by='auto'
  ).delete()

  for t in tasks_qs:
    blocks = schedule.get(t.name, [])
    for date_str, hour in blocks:
      start = datetime.fromisoformat(date_str) + timedelta(hours=hour)
      end = start + timedelta(hours=1)

      # Make the start and end times timezone aware
      start = timezone.make_aware(start)
      end = timezone.make_aware(end)

      ScheduledTask.objects.create(
        task=t,
        start_datetime=start,
        end_datetime=end,
        assigned_by='auto'
      )

  