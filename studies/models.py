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
    start_time = models.TimeField(help_text='e.g. 09:00')
    end_time = models.TimeField(help_text='e.g. 10:15')

    class Meta:
        ordering = ['name']
    
    def __str__(self):
        # day = dict(self.DAYS)[self.days_of_week]
        # return f'{self.name}: {day}{self.start_time:%H:%M}-{self.end_time:%H:%M}'
        days = [label for idx, label in self.DAYS if idx in self.days_of_week]
        return f'{self.name} ({','.join(days)}) {self.start_time:%H:%M}-{self.end_time:%H:%M}'

class Task(models.Model):
    owner = models.ForeignKey(
      settings.AUTH_USER_MODEL,
      on_delete=models.CASCADE,
      related_name='tasks'
    )
    name = models.CharField(max_length=100)
    due_date = models.DateField(null=True, blank=True)
    # Notes or description for the task !!!
    estimated_duration = models.DurationField(
        help_text='e.g. 1:30 for 1 hour 30 minutes'
    )
    class Meta:
        unique_together = ('owner', 'name')
        ordering = ['due_date']

    def __str__(self):
        return f'{self.name} (Due: {self.due_date})'