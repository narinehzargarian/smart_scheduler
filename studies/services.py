from datetime import datetime, timedelta, time
from django.utils import timezone
from django.db.models import Exists, OuterRef
# import pytz
from .utils import get_availability
from .algorithms import rule_based_scheduler
from .models import Task, ScheduledTask

# pt = pytz.timezone('America/Los_Angeles')

def generate_schedule(user):
  print('Generate schedule has been called!')
  ScheduledTask.objects.filter(
    task__owner=user,
    assigned_by='auto'
  ).delete()
  availability = get_availability(user)
  
  # Get the tasks with no user assigned schedule
  tasks = (
    Task.objects
    .filter(owner=user, due_date__isnull=False)
    .annotate(has_user_schedule=Exists(
      ScheduledTask.objects.filter(
        task=OuterRef('pk'),
        assigned_by='user'
      )
    ))
    .filter(has_user_schedule=False)
    .order_by('due_date')
  
  )
    

  # # Convert to list of dicts
  # tasks = [{
  #   'name': t.name,
  #   'due_date': t.due_date.strftime('%Y-%m-%d %I:%M %p'),
  #   'estimated_duration' : int(t.estimated_duration.total_seconds() // 3600)
  # } for t in tasks]

  schedule = rule_based_scheduler(calendar=availability, tasks=tasks)

  # # Delete the old auto schedule
  # ScheduledTask.objects.filter(
  #   task__owner=user,
  #   assigned_by='auto'
  # ).delete()

  for task, blocks in schedule.items():
    for date_str, hour in blocks:
      day = datetime.fromisoformat(date_str).date()
      start = timezone.make_aware(datetime.combine(day, time(hour)))
      end = start + timedelta(hours=1)

      ScheduledTask.objects.create(
        task=task,
        start_datetime=start,
        end_datetime=end,
        assigned_by='auto'
      )

  