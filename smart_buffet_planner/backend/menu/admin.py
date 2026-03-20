from django.contrib import admin
from .models import Category, Dish, Venue, VenueDish


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order']
    ordering = ['order']


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'quantity_per_person', 'unit', 'cost_per_unit',
                    'preparation_time', 'season', 'is_vegetarian', 'is_active']
    list_filter = ['category', 'season', 'is_vegetarian', 'is_active']
    search_fields = ['name']
    list_editable = ['is_active', 'cost_per_unit', 'quantity_per_person']


class VenueDishInline(admin.TabularInline):
    model = VenueDish
    extra = 3
    autocomplete_fields = ['dish']


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'contact', 'is_active']
    list_filter = ['is_active', 'city']
    search_fields = ['name', 'city']
    list_editable = ['is_active']
    inlines = [VenueDishInline]


@admin.register(VenueDish)
class VenueDishAdmin(admin.ModelAdmin):
    list_display = ['venue', 'dish', 'price_override']
    list_filter = ['venue']
    search_fields = ['venue__name', 'dish__name']
