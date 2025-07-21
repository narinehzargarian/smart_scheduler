from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Course, Task
from .serializers import CourseSerializer, TaskSerializer
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
        return Task.objects.filter(owner=self.request.user)

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
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        print('Raw payload: ', request.data)
        if not serializer.is_valid():
            print('task validation error: ', serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        return super().create(request, *args, **kwargs)
    

@api_view(['POST'])
def build_schedule(request):
  generate_schedule(request.user)
  return Response({'status': 'ok'}, status=status.HTTP_200_OK)