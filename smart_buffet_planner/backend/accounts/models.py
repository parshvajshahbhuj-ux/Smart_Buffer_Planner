from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('caterer', 'Caterer'),
        ('organizer', 'Event Organizer'),
        ('individual', 'Individual'),
    ]
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='organizer')
    phone = models.CharField(max_length=20, blank=True)
    organization = models.CharField(max_length=100, blank=True)

    # Caterer-specific
    profit_margin = models.DecimalField(max_digits=5, decimal_places=2, default=20.00,
                                        help_text="Default profit margin % for caterers")
    service_charge = models.DecimalField(max_digits=5, decimal_places=2, default=5.00,
                                         help_text="Service charge % added on top of food cost")

    # Individual-specific
    budget_cap = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                     help_text="Personal budget cap for individual users")
    dietary_preference = models.CharField(
        max_length=20,
        choices=[('all', 'No Preference'), ('vegetarian', 'Vegetarian'), ('vegan', 'Vegan')],
        default='all'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    @property
    def is_caterer(self):
        return self.role == 'caterer'

    @property
    def is_organizer(self):
        return self.role == 'organizer'

    @property
    def is_individual(self):
        return self.role == 'individual'
