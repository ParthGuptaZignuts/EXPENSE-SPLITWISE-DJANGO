from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Account
from .serializers import AccountSerializer


class AccountViewSet(viewsets.ViewSet):
    """CRUD operations for Account model"""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="List all accounts for the logged-in user",
        responses={200: AccountSerializer(many=True)},
    )
    @action(detail=False, methods=["get"], url_path="list")
    def list_accounts(self, request):
        """List all accounts for the logged-in user"""
        user = request.user
        accounts = Account.objects.filter(user=user)
        serializer = AccountSerializer(accounts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Create a new account",
        request=AccountSerializer,
        responses={201: AccountSerializer, 400: "Bad Request"},
    )
    @action(detail=False, methods=["post"], url_path="create")
    def create_account(self, request):
        """Create a new account for the logged-in user"""
        user = request.user
        account_type = request.data.get("account_type")

        # Check if the user already has an account with the same name
        if Account.objects.filter(user=user, account_type=account_type).exists():
            return Response(
                {
                    "error": f"You already have an account with the name '{account_type}'."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create the new account
        serializer = AccountSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Retrieve an account by ID",
        responses={200: AccountSerializer, 404: "Account not found"},
    )
    @action(detail=True, methods=["get"], url_path="retrieve")
    def retrieve_account(self, request, pk=None):
        """Retrieve an account by its ID for the logged-in user"""
        user = request.user
        account = get_object_or_404(Account, pk=pk, user=user)
        serializer = AccountSerializer(account)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Update an existing account",
        request=AccountSerializer,
        responses={
            200: AccountSerializer,
            400: "Bad Request",
            404: "Account not found",
        },
    )
    @action(detail=True, methods=["put"], url_path="update")
    def update_account(self, request, pk=None):
        """Update an existing account for the logged-in user"""
        user = request.user
        account = get_object_or_404(Account, pk=pk, user=user)
        serializer = AccountSerializer(account, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Delete an account",
        responses={204: "Account deleted", 404: "Account not found"},
    )
    @action(detail=True, methods=["delete"], url_path="delete")
    def delete_account(self, request, pk=None):
        """Delete an account for the logged-in user"""
        user = request.user
        account = get_object_or_404(Account, pk=pk, user=user)
        account.delete()
        return Response({"message": "Account deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
