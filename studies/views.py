from django.shortcuts import render
from django.utils import timezone
from django.db import transaction
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Course, Task, ScheduledTask
from .serializers import CourseSerializer, TaskSerializer, ScheduledTaskSerializer
from .services import generate_schedule

class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Course.objects.filter(owner=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
        generate_schedule(self.request.user)
    
    def perform_update(self, serializer):
        serializer.save()
        generate_schedule(self.request.user)

    def perform_destroy(self, instance):
        owner = instance.owner
        instance.delete()
        generate_schedule(owner)
    

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Delete any thing past due
        Task.objects.filter(
            owner=self.request.user,
            due_date__lt=timezone.now()
        ).delete()

        return Task.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
        generate_schedule(self.request.user)
    
    def perform_update(self, serializer):
        with transaction.atomic():
          task = serializer.save()
          ScheduledTask.objects.filter(
              task=task
          ).update(assigned_by='auto')

          generate_schedule(self.request.user)
    
    def perform_destroy(self, instance):
        owner = instance.owner
        instance.delete()
        generate_schedule(owner)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        print('Raw payload: ', request.data)
        if not serializer.is_valid():
            print('task validation error: ', serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        return super().create(request, *args, **kwargs)

class ScheduledTaskViewSet(viewsets.ModelViewSet):
    queryset = ScheduledTask.objects.all()
    serializer_class = ScheduledTaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ScheduledTask.objects.filter(task__owner=self.request.user)
    
    def perform_update(self, serializer):
        data = serializer.validated_data
        instance = serializer.instance

        # Verify the new scheduled times
        new_start = data.get('start_datetime', instance.start_datetime)
        new_end = data.get('end_datetime', instance.end_datetime)

        # Check it doesn't go past the task's due date
        due = instance.task.due_date
        if due and new_end > due:
            raise ValidationError('Cannot schedule beyond the task\'s due date.')

        # Schedules should not conflict
        conflicts = ScheduledTask.objects.filter(
            task__owner=self.request.user,
            start_datetime__lt=new_end,
            end_datetime__gt=new_start, 
        ).exclude(pk=instance.pk) # Ignore the update
        if conflicts.exists():
            raise ValidationError("This time slot conflicts with another scheduled task.")

        # Ensure it does not conflict with any courses on that day
        weekday = new_start.weekday()
        courses = Course.objects.filter(
            owner=self.request.user,
            start_date__lte=new_start.date(),
            end_date__gte=new_start.date(),
            days_of_week__contains=[weekday]
        )
        for course in courses:
            if (new_start.time() < course.end_time and
                new_end.time() > course.start_time):
                raise ValidationError(f'There is a conflict between {course.name} class and updated schedule.')
        

        # Save the updated as 'user'
        with transaction.atomic():
          serializer.save(assigned_by='user')
          task = instance.task
          # Mark all the schedules for the same task as 'user'
          ScheduledTask.objects.filter(task=task).exclude(assigned_by='user').update(assigned_by='user')

          # Delete the task if all the slots are completed
          any_incomplete = ScheduledTask.objects.filter(task=task, completed=False).exists()
          if not any_incomplete:
            task.delete()
    

@api_view(['POST'])
def build_schedule(request):
  generate_schedule(request.user)
  return Response({'status': 'ok'}, status=status.HTTP_200_OK)