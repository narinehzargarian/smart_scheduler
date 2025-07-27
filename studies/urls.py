from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, TaskViewSet, build_schedule, ScheduledTaskViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'scheduledtasks', ScheduledTaskViewSet, basename='scheduledtask')

urlpatterns = [
  path('', include(router.urls)),
  path('build_schedule/', build_schedule, name='build_schedule')
]
# urlpatterns = router.urls
