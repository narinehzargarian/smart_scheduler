from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Course, Task
from .serializers import CourseSerializer, TaskSerializer

class CourseViewSet(viewsets.ModelViewSet):
    print('in the course viewSet')
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Course.objects.filter(owner=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        # raw_data = request.data.copy()

        # if the due_date is in the past, raise a validation error
        # due_date_str = raw_data.get('due_date')
        # if due_date_str:
        #     due_date = parse_datetime(due_date_str)
        #     if due_date and due_date < datetime.now(due_date.tzinfo):
        #       return Response(
        #           {"due_date": "Due date cannot be in the past."},
        #           status=status.HTTP_400_BAD_REQUEST
        #       )
            
        print('Raw payload: ', request.data)
        if not serializer.is_valid():
            print('task validation error: ', serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        return super().create(request, *args, **kwargs)