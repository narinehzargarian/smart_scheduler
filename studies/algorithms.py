from datetime import datetime, time
from django.utils import timezone
from collections import defaultdict
import math

# Mock tasks
tasks = [
  {'name': 'homework 1', 'due_date': '2025-08-19 11:00 am', 'estimated_duration': 6},
  {'name': 'homework 2', 'due_date': '2025-08-07 2:30 pm', 'estimated_duration': 3},
  {'name': 'homework 3', 'due_date': '2025-09-01 12:00 am', 'estimated_duration': 2},
]

# TODO: use the backend data to get it
availability = {
    "2025-08-17": [9, 10, 11],
    "2025-08-18": [14, 15],
    "2025-08-19": [10, 11, 12],
    "2025-08-20": [9, 10]
}

def rule_based_scheduler(calendar, tasks):
  # calendar = {date: slots[:] for date, slots in availibility.items()}
  schedule = defaultdict(list)

  for task in tasks:
    due = timezone.localtime(task.due_date)
    # due = datetime.strptime(due_str, '%Y-%m-%d %I:%M %p')
    print(f'parsing {due}')
    total_hours = task.estimated_duration.total_seconds() / 3600
    hours_needed = math.ceil(total_hours)
    # time_needed = task['estimated_duration']
    # task_name = task['name']

    # Gather eligible time slots before deadline
    eligible_slots = []
    for date_str, slots in calendar.items():
      day = datetime.fromisoformat(date_str).date()
      for hour in slots:
        start_local_aware = timezone.make_aware(datetime.combine(day, time(hour)))
        start = timezone.localtime(start_local_aware)
        print('start of the task is ', start)
        if start < due:
          eligible_slots.append((start, date_str, hour))
    
      
    # Partial fallback if not enough slots
    if len(eligible_slots) < hours_needed:
      # schedule[task_name] =[(d, h) for _, d, h in eligible_slots] # Partial schedule
      for _, date_str, hour in eligible_slots:
        schedule[task].append((date_str, hour))
      continue

    grouped_slots = defaultdict(list)
    for slot_dt, date_str, hour in eligible_slots:
      grouped_slots[date_str].append((slot_dt, hour))
    
    assigned = 0 # Assigned hours to the task

    while assigned < hours_needed:
      for date in sorted(grouped_slots):
        if assigned >= hours_needed:
          break
        if grouped_slots[date]:
          slot_dt, hour = grouped_slots[date].pop(0)
          schedule[task].append((date, hour))
          calendar[date].remove(hour)
          assigned += 1
  
  return schedule


# sd = rule_based_scheduler(availability, tasks)
# print(sd)