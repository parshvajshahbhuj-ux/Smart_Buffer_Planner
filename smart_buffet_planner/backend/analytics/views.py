from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Avg, Count
from events.models import Event, EventMenu
from menu.models import Category


class DashboardAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        qs = Event.objects.filter(user=user) if not (user.is_staff or user.role == 'admin') \
            else Event.objects.all()

        total_events = qs.count()
        total_guests = qs.aggregate(total=Sum('guest_count'))['total'] or 0
        planned_events = qs.filter(status='planned').count()

        # Cost stats
        menu_qs = EventMenu.objects.filter(event__in=qs)
        total_spend = menu_qs.aggregate(total=Sum('total_cost'))['total'] or 0

        # Category distribution across all events
        cat_data = menu_qs.values('dish__category__name').annotate(
            total_qty=Sum('total_quantity_with_buffer'),
            total_cost=Sum('total_cost'),
            count=Count('id')
        ).order_by('-total_qty')

        # Event type distribution
        event_type_data = qs.values('event_type').annotate(count=Count('id'))

        # Monthly events trend (last 6 months)
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models.functions import TruncMonth
        six_months_ago = timezone.now().date() - timedelta(days=180)
        monthly_qs = (
            qs.filter(event_date__gte=six_months_ago)
            .annotate(month=TruncMonth('event_date'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )
        monthly = [
            {'month': m['month'].strftime('%Y-%m') if m['month'] else '', 'count': m['count']}
            for m in monthly_qs
        ]

        return Response({
            'summary': {
                'total_events': total_events,
                'planned_events': planned_events,
                'total_guests': total_guests,
                'total_spend': round(float(total_spend), 2),
            },
            'category_distribution': list(cat_data),
            'event_type_distribution': list(event_type_data),
            'monthly_trend': list(monthly),
        })


class EventAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, event_id):
        user = request.user
        try:
            if user.is_staff or user.role == 'admin':
                event = Event.objects.get(id=event_id)
            else:
                event = Event.objects.get(id=event_id, user=user)
        except Event.DoesNotExist:
            return Response({'error': 'Event not found'}, status=404)

        items = event.menu_items.select_related('dish__category').all()

        # Pie chart: category-wise quantity
        cat_qty = {}
        cat_cost = {}
        dish_labels = []
        dish_quantities = []
        dish_costs = []

        for item in items:
            cat = item.dish.category.name
            cat_qty[cat] = cat_qty.get(cat, 0) + float(item.total_quantity_with_buffer)
            cat_cost[cat] = cat_cost.get(cat, 0) + float(item.total_cost)
            dish_labels.append(item.dish.name)
            dish_quantities.append(float(item.total_quantity_with_buffer))
            dish_costs.append(float(item.total_cost))

        total_cost = sum(dish_costs)
        cost_per_guest = total_cost / event.guest_count if event.guest_count else 0

        # Waste risk
        buffer = float(event.buffer_percentage)
        waste_pct = buffer * 0.6
        waste_risk = 'Low' if waste_pct < 8 else ('Medium' if waste_pct < 15 else 'High')

        # Profit margin recommendation for caterers (safe for all roles)
        profit_margin = float(request.user.profit_margin or 0)
        recommended_price = cost_per_guest * (1 + profit_margin / 100) if profit_margin else cost_per_guest

        return Response({
            'event': {'id': event.id, 'name': event.name, 'guest_count': event.guest_count},
            'pie_chart': {
                'labels': list(cat_qty.keys()),
                'quantities': list(cat_qty.values()),
                'costs': list(cat_cost.values()),
            },
            'bar_chart': {
                'labels': dish_labels,
                'quantities': dish_quantities,
                'costs': dish_costs,
            },
            'summary': {
                'total_cost': round(total_cost, 2),
                'cost_per_guest': round(cost_per_guest, 2),
                'estimated_waste_pct': round(waste_pct, 2),
                'waste_risk': waste_risk,
                'recommended_price_per_guest': round(recommended_price, 2),
                'profit_margin_pct': profit_margin,
            }
        })


class PredictionView(APIView):
    """Learn from past events to suggest quantities."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        event_type = request.query_params.get('event_type')
        guest_count = int(request.query_params.get('guest_count', 100))

        qs = EventMenu.objects.filter(event__status='completed')
        if event_type:
            qs = qs.filter(event__event_type=event_type)

        suggestions = qs.values('dish__id', 'dish__name', 'dish__category__name').annotate(
            avg_qty_per_person=Avg('total_quantity') / Avg('event__guest_count'),
            usage_count=Count('id')
        ).order_by('-usage_count')[:20]

        return Response({
            'event_type': event_type,
            'guest_count': guest_count,
            'suggestions': [
                {
                    'dish_id': s['dish__id'],
                    'dish_name': s['dish__name'],
                    'category': s['dish__category__name'],
                    'avg_qty_per_person': round(float(s['avg_qty_per_person'] or 0), 2),
                    'suggested_total': round(float(s['avg_qty_per_person'] or 0) * guest_count, 2),
                    'popularity': s['usage_count'],
                }
                for s in suggestions
            ]
        })
