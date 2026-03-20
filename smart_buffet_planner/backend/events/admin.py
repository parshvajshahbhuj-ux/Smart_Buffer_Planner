from django.contrib import admin
from .models import Event, EventMenu


class EventMenuInline(admin.TabularInline):
    model = EventMenu
    extra = 0
    readonly_fields = ['total_quantity', 'total_quantity_with_buffer', 'total_cost']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'event_type', 'guest_count', 'event_date', 'status']
    list_filter = ['event_type', 'status']
    search_fields = ['name', 'user__email']
    inlines = [EventMenuInline]
