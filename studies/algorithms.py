from datetime import datetime, timedelta
from collections import defaultdict

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

def rule_based_scheduler(availibility, tasks):
  calendar = {date: slots[:] for date, slots in availibility.items()}
  schedule = defaultdict(list)

  for task in tasks:
    due_str = task['due_date']
    due = datetime.strptime(due_str, '%Y-%m-%d %I:%M %p')
    print(f'parsing {due_str}')
    time_needed = task['estimated_duration']
    task_name = task['name']

    # Gather eligible time slots before deadline
    eligible_slots = []
    for date, slots in calendar.items():
      for hour in slots:
        slot_dt = datetime.strptime(date, '%Y-%m-%d') + timedelta(hours=hour)
        if slot_dt < due:
          eligible_slots.append((slot_dt, date, hour))
    
      
    # Partial fallback if not enough slots
    if len(eligible_slots) < time_needed:
      schedule[task_name] =[(d, h) for _, d, h in eligible_slots] # Partial schedule
      for _, date, hour in eligible_slots:
        calendar[date].remove(hour)
      continue

    grouped_slots = defaultdict(list)
    for slot_dt, date_str, hour in eligible_slots:
      grouped_slots[date_str].append((slot_dt, hour))
    
    assigned = 0 # Assigned hours to the task

    while assigned < time_needed:
      for date in sorted(grouped_slots.keys()):
        if grouped_slots[date] and assigned < time_needed:
          slot_dt, hour = grouped_slots[date].pop(0)
          schedule[task_name].append((date, hour))
          calendar[date].remove(hour)
          assigned += 1
  
  return schedule


# sd = rule_based_scheduler(availability, tasks)
# print(sd)