from django.urls import path
from .views import PlanAPIView

urlpatterns = [
    path('', PlanAPIView.as_view(), name='generate_plan')
]
