from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Event, EventMenu
from .serializers import EventSerializer, EventCreateSerializer, MenuSubmitSerializer
from menu.models import Dish


class EventViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role == 'admin':
            return Event.objects.all().prefetch_related('menu_items__dish__category')
        return Event.objects.filter(user=user).prefetch_related('menu_items__dish__category')

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return EventCreateSerializer
        return EventSerializer

    @action(detail=True, methods=['post'])
    def submit_menu(self, request, pk=None):
        event = self.get_object()
        serializer = MenuSubmitSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        dish_ids = serializer.validated_data['dish_ids']
        overrides = serializer.validated_data.get('overrides', {})
        user = request.user

        dishes = Dish.objects.filter(id__in=dish_ids).select_related('category')

        # Individual: enforce dietary preference
        if user.role == 'individual' and user.dietary_preference == 'vegetarian':
            non_veg = [d.name for d in dishes if not d.is_vegetarian]
            if non_veg:
                return Response({
                    'error': f"Dietary preference is Vegetarian. Remove: {', '.join(non_veg)}"
                }, status=status.HTTP_400_BAD_REQUEST)

        # Category diversity warning
        category_counts = {}
        for dish in dishes:
            cat = dish.category.name
            category_counts[cat] = category_counts.get(cat, 0) + 1

        warnings = []
        for cat, count in category_counts.items():
            if count > 5:
                warnings.append(f"Too many dishes in '{cat}' ({count}). Consider diversifying.")

        # Individual: budget cap warning
        if user.role == 'individual':
            cap = event.personal_budget or (float(user.budget_cap) if user.budget_cap else None)
            if cap:
                estimated = sum(
                    float(d.quantity_per_person) * event.guest_count * float(d.cost_per_unit)
                    for d in dishes
                ) * (1 + float(event.buffer_percentage) / 100)
                if estimated > cap:
                    warnings.append(
                        f"Estimated cost ${estimated:.2f} exceeds budget cap ${cap:.2f}."
                    )

        event.menu_items.all().delete()
        menu_items = []
        for dish in dishes:
            override = overrides.get(str(dish.id))
            item = EventMenu(event=event, dish=dish, quantity_per_person_override=override)
            item.calculate()
            menu_items.append(item)

        EventMenu.objects.bulk_create(menu_items)
        event.status = 'planned'
        event.save()
        event.refresh_from_db()
        return Response({'event': EventSerializer(event).data, 'warnings': warnings})

    @action(detail=True, methods=['post'])
    def mark_complete(self, request, pk=None):
        """Organizer: mark event as completed."""
        event = self.get_object()
        if request.user.role not in ('organizer', 'admin') and not request.user.is_staff:
            return Response({'error': 'Only organizers can mark events complete.'}, status=403)
        event.status = 'completed'
        event.save()
        return Response({'status': 'completed'})

    @action(detail=True, methods=['patch'])
    def update_rsvp(self, request, pk=None):
        """Organizer: update confirmed RSVP count."""
        event = self.get_object()
        if request.user.role not in ('organizer', 'admin') and not request.user.is_staff:
            return Response({'error': 'Only organizers can update RSVP.'}, status=403)
        confirmed = request.data.get('confirmed_guests')
        if confirmed is None:
            return Response({'error': 'confirmed_guests required.'}, status=400)
        event.confirmed_guests = int(confirmed)
        event.save()
        return Response({'confirmed_guests': event.confirmed_guests})

    @action(detail=True, methods=['get'])
    def shopping_list(self, request, pk=None):
        """Caterer: ingredient shopping list with markup and service charge."""
        event = self.get_object()
        if request.user.role not in ('caterer', 'admin') and not request.user.is_staff:
            return Response({'error': 'Shopping list is a caterer-only feature.'}, status=403)

        items = event.menu_items.select_related('dish__category').all()
        user = request.user
        markup = float(event.markup_percentage or user.profit_margin)
        svc = float(event.service_charge or user.service_charge)

        grouped = {}
        total_raw = 0
        for item in items:
            cat = item.dish.category.name
            if cat not in grouped:
                grouped[cat] = []
            raw = float(item.total_cost)
            total_raw += raw
            grouped[cat].append({
                'dish': item.dish.name,
                'quantity': f"{float(item.total_quantity_with_buffer):.1f} {item.dish.unit}",
                'raw_cost': round(raw, 2),
            })

        after_markup = total_raw * (1 + markup / 100)
        client_total = after_markup * (1 + svc / 100)

        return Response({
            'event': event.name,
            'guest_count': event.guest_count,
            'shopping_list': grouped,
            'cost_summary': {
                'raw_food_cost': round(total_raw, 2),
                'markup_pct': markup,
                'after_markup': round(after_markup, 2),
                'service_charge_pct': svc,
                'client_total': round(client_total, 2),
                'profit': round(client_total - total_raw, 2),
                'per_guest': round(client_total / event.guest_count, 2) if event.guest_count else 0,
            }
        })

    @action(detail=True, methods=['get'])
    def calculations(self, request, pk=None):
        event = self.get_object()
        items = event.menu_items.select_related('dish__category').all()
        total_cost = sum(float(i.total_cost) for i in items)
        cost_per_guest = total_cost / event.guest_count if event.guest_count else 0

        buf = float(event.buffer_percentage)
        waste_pct = buf * 0.6
        waste_risk = 'Low' if waste_pct < 8 else ('Medium' if waste_pct < 15 else 'High')

        category_breakdown = {}
        for item in items:
            cat = item.dish.category.name
            if cat not in category_breakdown:
                category_breakdown[cat] = {'quantity': 0, 'cost': 0, 'dishes': []}
            category_breakdown[cat]['quantity'] += float(item.total_quantity_with_buffer)
            category_breakdown[cat]['cost'] += float(item.total_cost)
            category_breakdown[cat]['dishes'].append(item.dish.name)

        # Role-specific extras
        user = request.user
        extras = {}
        if user.role == 'caterer':
            markup = float(event.markup_percentage or user.profit_margin)
            svc = float(event.service_charge or user.service_charge)
            after_markup = total_cost * (1 + markup / 100)
            client_total = after_markup * (1 + svc / 100)
            extras = {
                'markup_pct': markup,
                'service_charge_pct': svc,
                'client_total': round(client_total, 2),
                'client_per_guest': round(client_total / event.guest_count, 2) if event.guest_count else 0,
                'profit': round(client_total - total_cost, 2),
            }
        elif user.role == 'organizer':
            extras = {
                'client_name': event.client_name,
                'client_email': event.client_email,
                'confirmed_guests': event.confirmed_guests,
                'rsvp_gap': event.guest_count - (event.confirmed_guests or 0),
            }
        elif user.role == 'individual':
            cap_raw = event.personal_budget or user.budget_cap
            cap = float(cap_raw) if cap_raw else None
            extras = {
                'personal_budget': cap,
                'budget_remaining': round(cap - total_cost, 2) if cap else None,
                'over_budget': (total_cost > cap) if cap else False,
            }

        return Response({
            'event_id': event.id,
            'event_name': event.name,
            'guest_count': event.guest_count,
            'total_cost': round(total_cost, 2),
            'cost_per_guest': round(cost_per_guest, 2),
            'estimated_waste_percentage': round(waste_pct, 2),
            'waste_risk': waste_risk,
            'buffer_percentage': buf,
            'category_breakdown': category_breakdown,
            'role_extras': extras,
            'items': [
                {
                    'dish': item.dish.name,
                    'category': item.dish.category.name,
                    'unit': item.dish.unit,
                    'qty_per_person': float(item.effective_qty_per_person),
                    'total_quantity': float(item.total_quantity),
                    'total_with_buffer': float(item.total_quantity_with_buffer),
                    'total_cost': float(item.total_cost),
                }
                for item in items
            ]
        })
