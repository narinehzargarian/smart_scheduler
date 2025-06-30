from rest_framework import serializers
from .models import Course, Task
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
    required=False,
    allow_null=True,
    input_formats=['%Y-%m-%d'],
    help_text='e.g. "2025-09-01"'
  )
  end_date = serializers.DateField(
    required=False,
    allow_null=True,
    input_formats=['%Y-%m-%d'],
    help_text='e.g. "2025-12-15"'
  )
  def validate(self, attrs):
    user = self.context['request'].user
    start_dt = attrs.get('start_time')
    end_time = attrs.get('end_time')
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
    required=False,
    allow_null=True,
    input_formats=[
      '%Y-%m-%d', # Date only
      '%Y-%m-%dT%H%M', # e.g. "2025-06-17T14:30"
      '%Y-%m-%d %H:%M', # e.g. "2025-06-17 14:30"
      '%Y-%m-%dT%I:%M %p', # e.g "2025-06-17T2:30 PM"
      '%Y-%m-%d %I:%M %p',  # e.g. "2025-06-17 2:30 PM"
    ],
    help_text='YYYY-MM-DD or with time "YYYY-MM-DDTHH:MM" "YYYY-MM-DD HH:MM AM/PM" omit/null for no due date'
  )
  class Meta:
    model = Task
    fields = [
      'id',
      'name',
      'due_date',
      'estimated_duration',
    ]
    read_only_fields = ['id']