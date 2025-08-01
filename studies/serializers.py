from django.utils import timezone
from rest_framework import serializers
from .models import Course, Task, ScheduledTask
from django.db.models import Q
import warnings

class CourseSerializer(serializers.ModelSerializer):
  start_time = serializers.TimeField(
    format='%I:%M %p',
    input_formats=['%I:%M %p', '%H:%M'],
    help_text='e.g. "9:00 AM" or "9:00"'
  )

  end_time = serializers.TimeField(
    format='%I:%M %p',
    input_formats=['%I:%M %p', '%H:%M'],
    help_text='e.g. "9:00 AM" or "9:00"'
  )
  start_date = serializers.DateField(
    # required=False,
    # allow_null=True,
    input_formats=['%Y-%m-%d'],
    help_text='e.g. "2025-09-01"'
  )
  end_date = serializers.DateField(
    # required=False,
    # allow_null=True,
    input_formats=['%Y-%m-%d'],
    help_text='e.g. "2025-12-15"'
  )
  def validate(self, attrs):
    user = self.context['request'].user
    start_dt = attrs.get('start_time')
    end_time = attrs.get('end_time')
    start_date = attrs.get('start_date')
    end_date = attrs.get('end_date')
    days = attrs.get('days_of_week')

    # Build a queryset of this user's courses
    qs = Course.objects.filter(owner=user)

    # If serializer is updating an existing instance
    if self.instance:
      qs = qs.exclude(pk=self.instance.pk)

    overlap = qs.filter(
      Q(days_of_week__overlap = days),
      start_time__lt=end_time,
      end_time__gt=start_dt
    ).exists()

    if overlap:
      warnings.warn('Course time overlaps with existing course.')
      raise serializers.ValidationError(
        'Course time overlaps with an existing course.'
      )
    
    if end_date < start_date:
      raise serializers.ValidationError({
        'end_date': 'End date must be on or after start date.'
      })

    return attrs
    
  
  class Meta:
    model = Course
    fields = [
      'id',
      'name',
      'days_of_week',
      'start_time',
      'end_time',
      'start_date',
      'end_date'
    ]
    read_only_fields = ['id']

class TaskSerializer(serializers.ModelSerializer):
  due_date = serializers.DateTimeField(
    required=True,
    allow_null=False,
    input_formats=[
      # '%Y-%m-%d', # Date only
      # '%Y-%m-%dT%H:%M', # e.g. "2025-06-17T14:30"
      # '%Y-%m-%d %H:%M', # e.g. "2025-06-17 14:30"
      # '%Y-%m-%dT%I:%M %p', # e.g "2025-06-17T2:30 PM"

      '%Y-%m-%d %I:%M %p',  # e.g. "2025-06-17 2:30 PM"
    ],
    help_text='Format: YYYY-MM-DD HH:MM AM/PM (e.g. "2025-08-19 5:00 PM")'
  )
  
  def validate(self, attrs):
    # Ensure due-date is not in the past
    due = attrs.get('due_date')
    if due and due < timezone.now():
      raise serializers.ValidationError({
        'due_date': 'Due date cannot be in the past.'
      })
    return attrs

  class Meta:
    model = Task
    fields = [
      'id',
      'name',
      'due_date',
      'estimated_duration',
    ]
    read_only_fields = ['id']

class ScheduledTaskSerializer(serializers.ModelSerializer):
  name = serializers.CharField(source="task.name", read_only=True)
  class Meta:
    model = ScheduledTask
    fields = [
      'id',
      'task',
      'name',
      'start_datetime',
      'end_datetime',
      'assigned_by',
      'completed'
    ]
    read_only_fields = ['assigend_by']