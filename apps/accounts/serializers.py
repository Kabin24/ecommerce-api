"""
Accounts app serializers for user registration, authentication, and profile management.
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, UserProfile, EmailVerificationToken
import uuid
from django.utils import timezone
from datetime import timedelta


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile data."""
    
    class Meta:
        model = UserProfile
        fields = [
            'bio', 'profile_picture', 'date_of_birth',
            'country', 'city', 'postal_code', 'address'
        ]


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user data (read-only)."""
    profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name',
            'phone_number', 'is_verified', 'is_staff',
            'profile', 'created_at'
        ]
        read_only_fields = ['id', 'is_staff', 'created_at', 'is_verified']


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Validates password confirmation and creates user account.
    """
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        help_text='Password must be at least 8 characters long'
    )
    password_confirm = serializers.CharField(
        write_only=True,
        min_length=8,
        help_text='Confirm password'
    )
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone_number', 'password', 'password_confirm']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate(self, attrs):
        """Validate password confirmation."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password': 'Passwords do not match.'
            })
        return attrs
    
    def create(self, validated_data):
        """Create user and send verification email."""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        # Create username from email
        user = User.objects.create_user(
            username=validated_data['email'],
            **validated_data
        )
        user.set_password(password)
        user.save()
        
        # Create user profile
        UserProfile.objects.create(user=user)
        
        # Create verification token
        token = str(uuid.uuid4())
        expires_at = timezone.now() + timedelta(hours=24)
        EmailVerificationToken.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )
        
        # TODO: Send verification email with token
        
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    Validates credentials and returns JWT tokens.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    def validate(self, attrs):
        """Authenticate user."""
        email = attrs.get('email')
        password = attrs.get('password')
        
        # Try to authenticate with email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({
                'email': 'User with this email does not exist.'
            })
        
        # Authenticate password
        if not user.check_password(password):
            raise serializers.ValidationError({
                'password': 'Invalid password.'
            })
        
        attrs['user'] = user
        return attrs


class TokenSerializer(serializers.Serializer):
    """Serializer for token responses."""
    access = serializers.CharField()
    refresh = serializers.CharField()


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password."""
    old_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        """Validate password change."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password': 'Passwords do not match.'
            })
        return attrs


class RefreshTokenSerializer(serializers.Serializer):
    """Serializer for token refresh."""
    refresh = serializers.CharField()


class LogoutSerializer(serializers.Serializer):
    """Serializer for logout (token blacklist)."""
    refresh = serializers.CharField()
