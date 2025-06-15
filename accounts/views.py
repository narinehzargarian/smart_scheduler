from django.shortcuts import render
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer
from django.conf import settings

class SignUpView(APIView):
   permission_classes = [] # Allow any user to register

   def post(self, request):
      serializer = RegisterSerializer(data=request.data)

      if serializer.is_valid():
         serializer.save()
         return Response({'detail': 'User created successfully'}, status=status.HTTP_201_CREATED)
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
   
# class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
#    username_field = 'email'

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
   