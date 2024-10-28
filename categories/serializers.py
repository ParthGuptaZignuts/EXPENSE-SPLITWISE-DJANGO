from rest_framework import serializers
from .models import Categories

class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = ['id', 'category_type', 'category_name']

    def validate(self, data):
        if not data.get('category_type'):
            raise serializers.ValidationError("The category_type field is required.")

        if data.get('category_type') not in ['EXPENSE', 'INCOME']:
            raise serializers.ValidationError("Invalid category_type. It must be 'EXPENSE' or 'INCOME'.")

        if data.get('category_name'):
            data['category_name'] = data['category_name'].strip().upper()

        return data

    def create(self, validated_data):
        validated_data['category_name'] = validated_data['category_name'].strip().upper()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'category_name' in validated_data:
            validated_data['category_name'] = validated_data['category_name'].strip().upper()
        return super().update(instance, validated_data)
