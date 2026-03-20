from django.db import models
from django.conf import settings
from menu.models import Dish, Venue


class Event(models.Model):
    EVENT_TYPES = [
        ('wedding', 'Wedding'),
        ('birthday', 'Birthday'),
        ('corporate', 'Corporate'),
        ('festival', 'Festival'),
        ('social', 'Social Gathering'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('planned', 'Planned'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='events')
    name = models.CharField(max_length=200)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    guest_count = models.PositiveIntegerField()
    event_date = models.DateField()
    venue = models.CharField(max_length=200, blank=True)
    venue_ref = models.ForeignKey(Venue, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='events', help_text="Linked venue for venue-specific menu")
    notes = models.TextField(blank=True)
    buffer_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')

    # Organizer-specific
    client_name = models.CharField(max_length=100, blank=True, help_text="Client name for organizers")
    client_email = models.EmailField(blank=True)
    client_phone = models.CharField(max_length=20, blank=True)
    confirmed_guests = models.PositiveIntegerField(null=True, blank=True,
                                                    help_text="Confirmed RSVP count")

    # Caterer-specific
    markup_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                             help_text="Per-event markup override for caterers")
    service_charge = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                          help_text="Per-event service charge override")

    # Individual-specific
    personal_budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                           help_text="Personal budget cap for this event")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-event_date']

    def __str__(self):
        return f"{self.name} ({self.event_type}) - {self.event_date}"


class EventMenu(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='menu_items')
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    quantity_per_person_override = models.DecimalField(max_digits=8, decimal_places=2,
                                                        null=True, blank=True)
    total_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_quantity_with_buffer = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        unique_together = ['event', 'dish']

    def __str__(self):
        return f"{self.event.name} - {self.dish.name}"

    @property
    def effective_qty_per_person(self):
        return self.quantity_per_person_override or self.dish.quantity_per_person

    def calculate(self):
        qty = float(self.effective_qty_per_person) * self.event.guest_count
        buf = float(self.event.buffer_percentage) / 100
        self.total_quantity = qty
        self.total_quantity_with_buffer = qty * (1 + buf)
        self.total_cost = self.total_quantity_with_buffer * float(self.dish.cost_per_unit)
        return self
