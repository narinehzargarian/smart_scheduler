from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import SignUpView, CookieTokenObtainPairView


urlpatterns = [
    path('login/', CookieTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]