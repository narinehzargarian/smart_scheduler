from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, TaskViewSet

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = router.urls
