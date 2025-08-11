from django.urls import path
from .views import SignUpView, CookieTokenObtainPairView, UserDeleteView, LogoutView, CurrentUserView, CookieTokenRefreshView



urlpatterns = [
  path('login/', CookieTokenObtainPairView.as_view(), name='token_obtain_pair'),
  path('user/', CurrentUserView.as_view(), name='current_user'),
  path('signup/', SignUpView.as_view(), name='signup'),
  path('token/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
  path('logout/', LogoutView.as_view(), name='logout'),
  path('delete/', UserDeleteView.as_view(), name='user_delete'),
]