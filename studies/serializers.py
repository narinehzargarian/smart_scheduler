from rest_framework import serializers
from .models import Course, Task

class CourseSerializer(serializers.ModelSerializer):
  class Meta:
    model = Course
    fields = [
      'id',
      'name',
      'days_of_week',
      'start_time',
      'end_time',
    ]
    read_only_fields = ['id']
class TaskSerializer(serializers.ModelSerializer):
  due_date = serializers.DateField(
    required=False,
    allow_null=True,
    input_formats=['%Y-%m-%d'],
    help_text='YYYY-MM-DD or omit/null for no due date'
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