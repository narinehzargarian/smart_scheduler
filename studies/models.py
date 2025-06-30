from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import ArrayField

class Course(models.Model):
    DAYS = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    owner = models.ForeignKey(
      settings.AUTH_USER_MODEL,
      on_delete=models.CASCADE,
      related_name='courses'
    )
    name = models.CharField(max_length=100)
    days_of_week = ArrayField(
        models.IntegerField(choices=DAYS),
        help_text='Lisf of days 0=Monday, 1=Tuesday, etc.'
    )
    start_time = models.TimeField(help_text='e.g. 09:00 AM')
    end_time = models.TimeField(help_text='e.g. 10:15 AM')

    start_date = models.DateField(
        blank=True,
        null=True,
        help_text='e.g. 2025-09-01')
    end_date = models.DateField(
        null=True, 
        blank=True,
        help_text='e.g. 2025-12-15'
    )
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        # day = dict(self.DAYS)[self.days_of_week]
        # return f'{self.name}: {day}{self.start_time:%H:%M}-{self.end_time:%H:%M}'
        days = [label for idx, label in self.DAYS if idx in self.days_of_week]
        start = self.start_time.strftime('%I:%M %p').lstrip('0')
        end = self.end_time.strftime('%I:%M %p').lstrip('0')
        return f'{self.name} ({','.join(days)}) {start}-{end}'

class Task(models.Model):
    owner = models.ForeignKey(
      settings.AUTH_USER_MODEL,
      on_delete=models.CASCADE,
      related_name='tasks'
    )
    name = models.CharField(max_length=100)
    due_date = models.DateTimeField(
        null=True, 
        blank=True,
        help_text='YYYY-MM-DD or YYYY-MM-DDTHH:MM[:SS]'
    )

    # Notes or description for the task !!!
    estimated_duration = models.DurationField(
        help_text='e.g. 1:30 for 1 hour 30 minutes'
    )
    class Meta:
        unique_together = ('owner', 'name')
        ordering = ['due_date']

    def __str__(self):
        if self.due_date:
            ds = self.due_date.strftime('%Y-%m-%d %I:%M %p').lstrip('0')
            return f'{self.name} (Due: {ds})'
        return self.name

class ScheduledTask(models.Model):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='scheduled_blocks'
    )
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    assigned_by = models.CharField(
        max_length=50,
        default='auto', # 'auto' or 'user'
        help_text='Who assigned this block',
    )

    completed = models.BooleanField(default=False)

    class Meta:
        ordering = ['start_datetime']
    
    def __str__(self):
        return f'Scheduled {self.task.name} on {self.task.start_datetime.strftime("%Y-%m-%d %I:%M %p")}'

