from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
 
from .models import Categories
from .serializers import CategoriesSerializer


class CategoriesViewSet(viewsets.ViewSet):
    """CRUD operations for Categories model"""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="List all categories for the logged-in user",
        parameters=[
            OpenApiParameter(
                name="category_type",
                description="Optional filter for category type (EXPENSE or INCOME).",
                required=False,
                type=str,
                enum=["EXPENSE", "INCOME"],
            )
        ],
        responses={200: CategoriesSerializer(many=True)},
    )
    @action(detail=False, methods=["get"], url_path="list")
    def list_categories(self, request):
        """List all categories for the logged-in user with optional filtering by category_type"""
        user = request.user
        category_type = request.query_params.get("category_type").upper()

        if category_type:
            if category_type not in ["EXPENSE", "INCOME"]:
                return Response(
                    {"error": "Invalid category_type. Must be 'EXPENSE' or 'INCOME'."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            categories = Categories.objects.filter(
                user=user, category_type=category_type
            )
        else:
            categories = Categories.objects.filter(user=user)

        serializer = CategoriesSerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Create a new category",
        request=CategoriesSerializer,
        responses={201: CategoriesSerializer, 400: "Bad Request"},
    )
    @action(detail=False, methods=["post"], url_path="create")
    def create_category(self, request):
        """Create a new category for the logged-in user"""
        user = request.user
        category_name = request.data.get("category_name", "").strip().strip().upper()
        category_type = request.data.get("category_type", "").strip().strip().upper()

        if not category_name or not category_type:
            return Response(
                {"error": "Both category_name and category_type are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if Categories.objects.filter(
            user=user, category_name=category_name, category_type=category_type
        ).exists():
            return Response(
                {"error": "This category already exists for the user."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = CategoriesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Retrieve a category by ID",
        responses={200: CategoriesSerializer, 404: "Category not found"},
    )
    @action(detail=True, methods=["get"], url_path="retrieve")
    def retrieve_category(self, request, pk=None):
        """Retrieve a category by its ID for the logged-in user"""
        user = request.user
        category = get_object_or_404(Categories, pk=pk, user=user)
        serializer = CategoriesSerializer(category)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Update an existing category",
        request=CategoriesSerializer,
        responses={
            200: CategoriesSerializer,
            400: "Bad Request",
            404: "Category not found",
            409: "Conflict: Category with this name already exists for the user",
        },
    )
    @action(detail=True, methods=["put"], url_path="update")
    def update_category(self, request, pk=None):
        """Update an existing category for the logged-in user"""
        user = request.user
        category = get_object_or_404(Categories, pk=pk, user=user)

        new_category_name = request.data.get("category_name")
        new_category_type = request.data.get("category_type")

        if (
            new_category_name
            and Categories.objects.filter(
                user=user,
                category_name=new_category_name,
                category_type=new_category_type,
            )
            .exclude(pk=category.pk)
            .exists()
        ):
            return Response(
                {"error": "Category with this name already exists for the user."},
                status=status.HTTP_409_CONFLICT,
            )

        serializer = CategoriesSerializer(category, data=request.data, partial=True)

        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            except IntegrityError:
                return Response(
                    {"error": "Unable to update category due to integrity error."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Delete a category",
        responses={204: "Category deleted", 404: "Category not found"},
    )
    @action(detail=True, methods=["delete"], url_path="delete")
    def delete_category(self, request, pk=None):
        """Delete a category for the logged-in user"""
        user = request.user
        category = get_object_or_404(Categories, pk=pk, user=user)
        category.delete()
        return Response(
            {"message": "Category deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )
