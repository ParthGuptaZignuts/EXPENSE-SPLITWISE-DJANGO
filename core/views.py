from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from .models import UserDetails
from .serializers import ChangePasswordSerializer, UserDetailsSerializer, UserSerializer

from accounts.models import Account


class AuthViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]

    @extend_schema(
        summary="Register a new user",
        request=UserSerializer,
        responses={201: UserSerializer, 400: "Bad Request"},
    )
    @action(detail=False, methods=["post"], url_path="signup")
    def signup(self, request):
        """Register a new user"""
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            UserDetails.objects.create(user=user)
            Account.objects.create(user=user)
            return Response(
                {"message": "User created successfully."},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Login to get JWT token",
        request={
            "username": str,
            "password": str,
        },
        responses={200: "JWT Token returned", 401: "Invalid credentials"},
    )
    @action(detail=False, methods=["post"], url_path="login")
    def login(self, request):
        """Login and return a JWT token"""
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(request, username=username, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {"error": "Invalid username or password."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    @extend_schema(
        summary="Log out and blacklist the token",
        request={"refresh_token": str},
        responses={205: "Logged out successfully", 400: "Bad request"},
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="logout",
        permission_classes=[IsAuthenticated],
    )
    def logout(self, request):
        """Log out by blacklisting the token"""
        try:
            refresh_token = request.data.get("refresh_token")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"message": "Logged out successfully."},
                status=status.HTTP_205_RESET_CONTENT,
            )
        except Exception as e:
            return Response(
                {"error": "Bad request"}, status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        summary="Change password for logged-in user",
        request=ChangePasswordSerializer,
        responses={200: "Password updated successfully", 400: "Bad request"},
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="change-password",
        permission_classes=[IsAuthenticated],
    )
    def change_password(self, request):
        """Allow authenticated users to change their password"""
        user = request.user
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            if not user.check_password(serializer.validated_data["old_password"]):
                return Response(
                    {"error": "Wrong password."}, status=status.HTTP_400_BAD_REQUEST
                )
            user.set_password(serializer.validated_data["new_password"])
            user.save()
            return Response(
                {"message": "Password updated successfully."}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Send password reset email",
        request={"email": str},
        responses={200: "Password reset email sent", 404: "User not found"},
    )
    @action(detail=False, methods=["post"], url_path="forget-password")
    def forget_password(self, request):
        """Send email with password reset link even if the user is logged in"""
        email = request.data.get("email")
        user = get_object_or_404(User, email=email)

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        reset_link = f"{self.request.scheme}://{self.request.get_host()}/auth/reset-password/{uid}/{token}/"

        context = {"user": user, "reset_link": reset_link}
        email_body = render_to_string("password_reset_email.html", context)

        send_mail(
            "Password Reset",
            email_body,
            "noreply@example.com",
            [email],
            fail_silently=False,
            html_message=email_body,
        )

        return Response(
            {"message": "Password reset email sent."}, status=status.HTTP_200_OK
        )

    @extend_schema(
        summary="Reset password using token",
        request=None,
        responses={200: "Password reset successfully", 400: "Invalid token or user"},
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="reset-password/(?P<uidb64>[^/.]+)/(?P<token>[^/.]+)",
    )
    def reset_password(self, request, uidb64, token):
        """Reset password for a user"""
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user and default_token_generator.check_token(user, token):
            password = request.data.get("new_password")
            user.set_password(password)
            user.save()
            return Response(
                {"message": "Password reset successfully."}, status=status.HTTP_200_OK
            )
        return Response(
            {"error": "Invalid token or user."}, status=status.HTTP_400_BAD_REQUEST
        )

    @extend_schema(
        summary="Delete account of logged-in user",
        request=None,
        responses={204: "Account deleted successfully", 400: "Bad request"},
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="delete-account",
        permission_classes=[IsAuthenticated],
    )
    def delete_account(self, request):
        """Allow authenticated users to delete their account"""
        user = request.user
        user.delete()
        return Response(
            {"message": "User Account deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )

    @extend_schema(
        summary="Update profile for logged-in user",
        request=UserDetailsSerializer,
        responses={200: "Profile updated successfully", 400: "Bad request"},
    )
    @action(
        detail=False,
        methods=["put"],
        url_path="update-profile",
        permission_classes=[IsAuthenticated],
    )
    def update_profile(self, request):
        """Allow authenticated users to update their profile"""
        user = request.user
        user_details = get_object_or_404(UserDetails, user=user)
        serializer = UserDetailsSerializer(
            user_details, data=request.data, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Profile updated successfully."}, status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
