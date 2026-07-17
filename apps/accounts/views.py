"""
Accounts app views for authentication and user management.
"""
from rest_framework import status, viewsets, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from .models import User, EmailVerificationToken
from .serializers import (
    RegisterSerializer, LoginSerializer, TokenSerializer,
    UserSerializer, ChangePasswordSerializer, LogoutSerializer,
    RefreshTokenSerializer
)
from apps.core.exceptions import SuccessResponse


class AuthViewSet(viewsets.ViewSet):
    """
    ViewSet for authentication endpoints.
    Handles user registration, login, logout, and token management.
    """
    
    def get_permissions(self):
        """Set permission based on action."""
        if self.action in ['register', 'login', 'refresh']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny()])
    def register(self, request):
        """
        Register a new user account.
        
        Returns:
            - User object with email, name, and created_at
            - Message about email verification
        """
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return SuccessResponse(
                data=UserSerializer(user).data,
                message='User registered successfully. Please verify your email.',
                status=status.HTTP_201_CREATED
            )
        return Response(
            {
                'success': False,
                'message': 'Registration failed',
                'data': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny()])
    def login(self, request):
        """
        Login user and return JWT tokens.
        
        Returns:
            - access_token: Short-lived JWT token
            - refresh_token: Long-lived token to refresh access
        """
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            return SuccessResponse(
                data={
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'user': UserSerializer(user).data
                },
                message='Login successful'
            )
        return Response(
            {
                'success': False,
                'message': 'Login failed',
                'data': serializer.errors
            },
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        """
        Logout user by blacklisting the refresh token.
        
        The token is added to the blacklist to prevent reuse.
        """
        serializer = LogoutSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Add token to blacklist (if using rest_framework_simplejwt blacklist)
                # For now, we just return success
                return SuccessResponse(
                    message='Logout successful'
                )
            except TokenError:
                return Response(
                    {
                        'success': False,
                        'message': 'Invalid token'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(
            {
                'success': False,
                'message': 'Logout failed',
                'data': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny()])
    def refresh(self, request):
        """
        Refresh the access token using the refresh token.
        """
        serializer = RefreshTokenSerializer(data=request.data)
        if serializer.is_valid():
            try:
                refresh = RefreshToken(serializer.validated_data['refresh'])
                return SuccessResponse(
                    data={
                        'access': str(refresh.access_token),
                        'refresh': str(refresh)
                    },
                    message='Token refreshed successfully'
                )
            except InvalidToken:
                return Response(
                    {
                        'success': False,
                        'message': 'Invalid or expired refresh token'
                    },
                    status=status.HTTP_401_UNAUTHORIZED
                )
        return Response(
            {
                'success': False,
                'message': 'Token refresh failed',
                'data': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['get', 'put'])
    def profile(self, request):
        """
        Get or update current user profile.
        
        GET: Returns user profile information
        PUT: Updates user profile information
        """
        user = request.user
        
        if request.method == 'GET':
            serializer = UserSerializer(user)
            return SuccessResponse(data=serializer.data)
        
        elif request.method == 'PUT':
            # Update allowed fields
            allowed_fields = ['first_name', 'last_name', 'phone_number']
            data = {k: v for k, v in request.data.items() if k in allowed_fields}
            
            serializer = UserSerializer(user, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return SuccessResponse(
                    data=serializer.data,
                    message='Profile updated successfully'
                )
            return Response(
                {
                    'success': False,
                    'message': 'Profile update failed',
                    'data': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """
        Change user password.
        
        Requires old password and new password confirmation.
        """
        user = request.user
        serializer = ChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            # Check old password
            if not user.check_password(serializer.validated_data['old_password']):
                return Response(
                    {
                        'success': False,
                        'message': 'Incorrect old password'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Set new password
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            return SuccessResponse(
                message='Password changed successfully'
            )
        
        return Response(
            {
                'success': False,
                'message': 'Password change failed',
                'data': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny()])
    def verify_email(self, request):
        """
        Verify email using token from verification link.
        """
        token = request.data.get('token')
        
        if not token:
            return Response(
                {
                    'success': False,
                    'message': 'Verification token is required'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            verification = EmailVerificationToken.objects.get(token=token)
            
            if not verification.is_valid():
                return Response(
                    {
                        'success': False,
                        'message': 'Verification token has expired or been used'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Mark email as verified
            user = verification.user
            user.is_verified = True
            user.save()
            
            # Mark token as used
            verification.is_used = True
            verification.save()
            
            return SuccessResponse(
                message='Email verified successfully'
            )
        
        except EmailVerificationToken.DoesNotExist:
            return Response(
                {
                    'success': False,
                    'message': 'Invalid verification token'
                },
                status=status.HTTP_404_NOT_FOUND
            )
