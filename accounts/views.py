from django.shortcuts import render
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework import status, permissions, generics
from .serializers import RegisterSerializer
from .serializers import RegisterSerializer
from django.conf import settings
from django.contrib.auth import get_user_model

user = get_user_model()

class SignUpView(APIView):
   permission_classes = [] # Allow any user to register

   def post(self, request):
      serializer = RegisterSerializer(data=request.data)

      if serializer.is_valid():
         serializer.save()
         return Response({'detail': 'User created successfully'}, status=status.HTTP_201_CREATED)
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# GET /api/auth/user/ -> returns the current user data
class CurrentUserView(generics.RetrieveAPIView):
  serializer_class = RegisterSerializer
  permission_classes = [permissions.IsAuthenticated]

  def get_object(self):
     print(self.request.user)
     return self.request.user

class CookieTokenObtainPairView(TokenObtainPairView):
  #  serializer_class = EmailTokenObtainPairSerializer
   
   def post(self, request, *args, **kwargs):
      original_response = super().post(request, *args, **kwargs)

      # Extract tokens from the original response
      access = original_response.data.get('access')
      refresh = original_response.data.get('refresh')

      # Set the refresh token as an HttpOnly cookie
      if refresh:
         original_response.set_cookie(
            'refresh_token',
             refresh,
             max_age=60 * 60 * 24 * 7,  # 7 days
             httponly=True,
             secure=not settings.DEBUG,  # Use secure cookies in production
             samesite='Lax'  # Adjust as needed
         )
      # Retrun the response
      # return Response({
      #    'access': access,
      # }, status=original_response.status_code)
      original_response.data = {
         'access': access
      }
      return original_response

  #  def finalize_response(self, request, response, *args, **kwargs):
  #     # Get the refresh token
  #     refresh = response.data.get('refresh')
  #     if refresh:
  #        # Set refresh token as HttpOnly cookie
  #         response.set_cookie(
  #            'refresh_token',
  #            refresh,
  #            max_age=60 * 60 * 24 * 7,  # 7 days
  #            httponly=True,
  #            secure=not settings.DEBUG,  # Use secure cookies in production
  #            samesite='Lax'  # Adjust as needed
  #         )
  #         # Remove the refresh token from the response data
  #         del response.data['refresh']
  #     return super().finalize_response(request, response, *args, **kwargs)

class LogoutView(APIView):
  permission_classes = [permissions.IsAuthenticated]
  
  def post(self, request):
    raw_token = request.COOKIES.get('refresh_token')

    if not raw_token:
       return Response({'detail': 'No refresh token found'}, 
                       status=status.HTTP_400_BAD_REQUEST
                      )

    try:
       token = RefreshToken(raw_token)
       token.blacklist()
    except Exception:
       return Response({'detail': 'Invalid token'}, 
                       status=status.HTTP_400_BAD_REQUEST
                      )

    resp = Response(status=status.HTTP_204_NO_CONTENT)
    resp.delete_cookie('refresh_token')
    return resp

class CookieTokenRefreshView(TokenRefreshView):
   # POST /auth/token/refresh
   def post(self, request, *args, **kwargs):
      refresh = request.COOKIES.get('refresh_token')
      if not refresh:
         return Response({'detail' : 'No refresh token'}, status=400)
      
      serializer = self.get_serializer(data={'refresh': refresh})
      serializer.is_valid(raise_exception=True)
      data = serializer.validated_data
      return Response({'access': data['access']})

class UserDeleteView(APIView):
   permission_classes = [permissions.IsAuthenticated]

   def delete(self, request):
      user = request.user
      user.delete()
      return Response(status=status.HTTP_204_NO_CONTENT)