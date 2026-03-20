from django.db import models


class Venue(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=300, blank=True)
    city = models.CharField(max_length=100, blank=True)
    contact = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Dish(models.Model):
    SEASON_CHOICES = [
        ('all', 'All Seasons'),
        ('summer', 'Summer'),
        ('winter', 'Winter'),
        ('monsoon', 'Monsoon'),
    ]
    UNIT_CHOICES = [
        ('grams', 'Grams'),
        ('ml', 'Milliliters'),
        ('units', 'Units'),
    ]

    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='dishes')
    quantity_per_person = models.DecimalField(max_digits=8, decimal_places=2,
                                               help_text="Quantity per person in grams/ml/units")
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='grams')
    cost_per_unit = models.DecimalField(max_digits=10, decimal_places=2,
                                         help_text="Cost per gram/ml/unit")
    preparation_time = models.PositiveIntegerField(help_text="Preparation time in minutes")
    season = models.CharField(max_length=10, choices=SEASON_CHOICES, default='all')
    is_vegetarian = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} ({self.category})"

    @property
    def cost_per_person(self):
        return float(self.quantity_per_person) * float(self.cost_per_unit)


class VenueDish(models.Model):
    """Links a Venue to the Dishes it offers, with optional venue-specific pricing."""
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='venue_dishes')
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, related_name='venue_dishes')
    price_override = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                          help_text="Venue-specific cost per unit (overrides dish default)")

    class Meta:
        unique_together = ['venue', 'dish']

    def __str__(self):
        return f"{self.venue.name} — {self.dish.name}"
