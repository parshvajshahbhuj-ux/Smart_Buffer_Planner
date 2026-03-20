from rest_framework import serializers
from .models import Event, EventMenu
from menu.serializers import DishWithCategorySerializer


class EventMenuSerializer(serializers.ModelSerializer):
    dish_detail = DishWithCategorySerializer(source='dish', read_only=True)
    effective_qty_per_person = serializers.ReadOnlyField()

    class Meta:
        model = EventMenu
        fields = ['id', 'dish', 'dish_detail', 'quantity_per_person_override',
                  'effective_qty_per_person', 'total_quantity',
                  'total_quantity_with_buffer', 'total_cost']
        read_only_fields = ['total_quantity', 'total_quantity_with_buffer', 'total_cost']


class EventSerializer(serializers.ModelSerializer):
    menu_items = EventMenuSerializer(many=True, read_only=True)
    total_cost = serializers.SerializerMethodField()
    cost_per_guest = serializers.SerializerMethodField()
    waste_risk = serializers.SerializerMethodField()
    venue_name = serializers.CharField(source='venue_ref.name', read_only=True, default=None)

    class Meta:
        model = Event
        fields = ['id', 'name', 'event_type', 'guest_count', 'event_date', 'venue', 'venue_ref', 'venue_name',
                  'notes', 'buffer_percentage', 'status',
                  'client_name', 'client_email', 'client_phone', 'confirmed_guests',
                  'markup_percentage', 'service_charge', 'personal_budget',
                  'menu_items', 'total_cost', 'cost_per_guest', 'waste_risk', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_total_cost(self, obj):
        return float(sum(item.total_cost for item in obj.menu_items.all()))

    def get_cost_per_guest(self, obj):
        total = self.get_total_cost(obj)
        return round(total / obj.guest_count, 2) if obj.guest_count else 0

    def get_waste_risk(self, obj):
        buffer = float(obj.buffer_percentage)
        if buffer <= 10:
            return 'Low'
        elif buffer <= 20:
            return 'Medium'
        return 'High'


class EventCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'name', 'event_type', 'guest_count', 'event_date', 'venue', 'venue_ref',
                  'notes', 'buffer_percentage', 'status',
                  # organizer
                  'client_name', 'client_email', 'client_phone', 'confirmed_guests',
                  # caterer
                  'markup_percentage', 'service_charge',
                  # individual
                  'personal_budget']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class MenuSubmitSerializer(serializers.Serializer):
    dish_ids = serializers.ListField(child=serializers.IntegerField(), min_length=1)
    overrides = serializers.DictField(child=serializers.DecimalField(max_digits=8, decimal_places=2),
                                       required=False, default=dict)
