from rest_framework import serializers
from .models import Category, Dish, Venue, VenueDish


class CategorySerializer(serializers.ModelSerializer):
    dish_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'order', 'dish_count']

    def get_dish_count(self, obj):
        return obj.dishes.filter(is_active=True).count()


class DishSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    cost_per_person = serializers.ReadOnlyField()

    class Meta:
        model = Dish
        fields = ['id', 'name', 'category', 'category_name', 'quantity_per_person',
                  'unit', 'cost_per_unit', 'cost_per_person', 'preparation_time',
                  'season', 'is_vegetarian', 'is_active', 'description']


class DishWithCategorySerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    cost_per_person = serializers.ReadOnlyField()

    class Meta:
        model = Dish
        fields = ['id', 'name', 'category', 'quantity_per_person', 'unit',
                  'cost_per_unit', 'cost_per_person', 'preparation_time',
                  'season', 'is_vegetarian', 'is_active', 'description']


class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = ['id', 'name', 'address', 'city', 'contact']
