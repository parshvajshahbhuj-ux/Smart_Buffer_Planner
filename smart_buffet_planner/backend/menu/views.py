from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Dish, Venue, VenueDish
from .serializers import CategorySerializer, DishSerializer, DishWithCategorySerializer, VenueSerializer


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and (request.user.is_staff or request.user.role == 'admin')


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

    @action(detail=True, methods=['get'])
    def dishes(self, request, pk=None):
        category = self.get_object()
        dishes = category.dishes.filter(is_active=True)
        serializer = DishSerializer(dishes, many=True)
        return Response(serializer.data)


class DishViewSet(viewsets.ModelViewSet):
    queryset = Dish.objects.filter(is_active=True).select_related('category')
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'season', 'is_vegetarian']
    search_fields = ['name', 'description']

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return DishWithCategorySerializer
        return DishSerializer

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        categories = Category.objects.prefetch_related('dishes').all()
        result = []
        for cat in categories:
            dishes = cat.dishes.filter(is_active=True)
            result.append({
                'category': CategorySerializer(cat).data,
                'dishes': DishSerializer(dishes, many=True).data,
            })
        return Response(result)

    @action(detail=False, methods=['get'])
    def seasonal_suggestions(self, request):
        from datetime import date
        month = date.today().month
        if month in [3, 4, 5, 6]:
            season = 'summer'
        elif month in [7, 8, 9]:
            season = 'monsoon'
        else:
            season = 'winter'
        dishes = Dish.objects.filter(is_active=True, season__in=[season, 'all'])
        return Response({
            'season': season,
            'dishes': DishSerializer(dishes, many=True).data
        })


class VenueViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Venue.objects.filter(is_active=True)
    serializer_class = VenueSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'city']

    @action(detail=False, methods=['post'])
    def from_osm(self, request):
        """Auto-create a Venue from OSM data and assign a smart default menu."""
        name = request.data.get('name', '').strip()
        address = request.data.get('address', '').strip()
        city = request.data.get('city', '').strip()
        osm_id = request.data.get('osm_id', '')

        if not name:
            return Response({'error': 'name is required'}, status=400)

        # Check if already exists (match by name + city)
        existing = Venue.objects.filter(name__iexact=name, city__iexact=city).first()
        if existing:
            return Response({'id': existing.id, 'name': existing.name, 'created': False})

        # Create new venue
        venue = Venue.objects.create(name=name, address=address, city=city)

        # Assign smart default menu based on city
        self._assign_default_menu(venue, city)

        return Response({'id': venue.id, 'name': venue.name, 'created': True})

    def _assign_default_menu(self, venue, city):
        """Assign dishes to a new venue based on city — all dishes as default."""
        city_lower = city.lower()

        # City-based dish selection logic
        if any(c in city_lower for c in ['mumbai', 'pune', 'goa']):
            preferred_dishes = [
                'Paneer Tikka', 'Butter Chicken', 'Dal Makhani', 'Biryani',
                'Garlic Naan', 'Steamed Rice', 'Gulab Jamun', 'Mango Lassi',
                'Masala Chai', 'Soft Drinks', 'Caesar Salad', 'Vegetable Spring Rolls',
            ]
        elif any(c in city_lower for c in ['delhi', 'agra', 'lucknow', 'jaipur']):
            preferred_dishes = [
                'Chicken Tikka', 'Butter Chicken', 'Dal Makhani', 'Biryani',
                'Garlic Naan', 'Steamed Rice', 'Gulab Jamun', 'Masala Chai',
                'Soft Drinks', 'Greek Salad', 'Dinner Rolls', 'Soup of the Day',
            ]
        elif any(c in city_lower for c in ['bangalore', 'bengaluru', 'chennai', 'hyderabad']):
            preferred_dishes = [
                'Vegetable Spring Rolls', 'Palak Paneer', 'Pasta Arrabiata',
                'Grilled Fish', 'Steamed Rice', 'Garlic Naan', 'Fruit Salad',
                'Lemonade', 'Masala Chai', 'Caesar Salad', 'Bruschetta',
            ]
        else:
            # Default: assign all active dishes
            preferred_dishes = list(
                Dish.objects.filter(is_active=True).values_list('name', flat=True)
            )

        for dish_name in preferred_dishes:
            try:
                dish = Dish.objects.get(name=dish_name, is_active=True)
                VenueDish.objects.get_or_create(venue=venue, dish=dish)
            except Dish.DoesNotExist:
                pass

    @action(detail=True, methods=['get'])
    def dishes(self, request, pk=None):
        """Return dishes for this venue grouped by category."""
        venue = self.get_object()
        venue_dishes = VenueDish.objects.filter(venue=venue).select_related(
            'dish__category'
        )

        # Group by category, apply price override if set
        cat_map = {}
        for vd in venue_dishes:
            dish = vd.dish
            if not dish.is_active:
                continue
            cat_name = dish.category.name
            if cat_name not in cat_map:
                cat_map[cat_name] = {
                    'category': {'id': dish.category.id, 'name': cat_name, 'order': dish.category.order},
                    'dishes': []
                }
            # Build dish dict with optional price override
            effective_cost = float(vd.price_override or dish.cost_per_unit)
            cat_map[cat_name]['dishes'].append({
                'id': dish.id,
                'name': dish.name,
                'category': {'id': dish.category.id, 'name': cat_name, 'order': dish.category.order},
                'quantity_per_person': float(dish.quantity_per_person),
                'unit': dish.unit,
                'cost_per_unit': effective_cost,
                'cost_per_person': float(dish.quantity_per_person) * effective_cost,
                'preparation_time': dish.preparation_time,
                'season': dish.season,
                'is_vegetarian': dish.is_vegetarian,
                'is_active': dish.is_active,
                'description': dish.description,
            })

        result = sorted(cat_map.values(), key=lambda x: x['category']['order'])
        return Response(result)
