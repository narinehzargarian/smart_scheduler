from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, TaskViewSet, build_schedule
from django.urls import path, include

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = [
  path('', include(router.urls)),
  path('build_schedule/', build_schedule, name='build_schedule')
]
# urlpatterns = router.urls
