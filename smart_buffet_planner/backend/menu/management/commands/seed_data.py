from django.core.management.base import BaseCommand
from menu.models import Category, Dish, Venue, VenueDish


CATEGORIES = [
    ('Starter', 1), ('Main Course', 2), ('Dessert', 3),
    ('Beverage', 4), ('Salad', 5), ('Bread & Rice', 6),
]

DISHES = [
    # (name, category_name, qty_per_person, unit, cost_per_unit, prep_time, season, is_veg, desc)
    ('Vegetable Spring Rolls', 'Starter', 80, 'grams', 0.015, 30, 'all', True, 'Crispy vegetable spring rolls'),
    ('Chicken Tikka', 'Starter', 100, 'grams', 0.025, 45, 'all', False, 'Marinated grilled chicken'),
    ('Paneer Tikka', 'Starter', 90, 'grams', 0.020, 35, 'all', True, 'Grilled cottage cheese'),
    ('Soup of the Day', 'Starter', 150, 'ml', 0.008, 20, 'winter', True, 'Warm seasonal soup'),
    ('Bruschetta', 'Starter', 60, 'grams', 0.012, 15, 'summer', True, 'Toasted bread with tomatoes'),
    ('Butter Chicken', 'Main Course', 200, 'grams', 0.022, 60, 'all', False, 'Creamy tomato chicken curry'),
    ('Dal Makhani', 'Main Course', 180, 'grams', 0.010, 90, 'winter', True, 'Slow-cooked black lentils'),
    ('Palak Paneer', 'Main Course', 180, 'grams', 0.018, 40, 'all', True, 'Spinach and cottage cheese'),
    ('Grilled Fish', 'Main Course', 200, 'grams', 0.030, 30, 'all', False, 'Herb-marinated grilled fish'),
    ('Pasta Arrabiata', 'Main Course', 200, 'grams', 0.012, 25, 'all', True, 'Spicy tomato pasta'),
    ('Biryani', 'Main Course', 250, 'grams', 0.018, 90, 'all', False, 'Aromatic rice dish'),
    ('Gulab Jamun', 'Dessert', 80, 'grams', 0.014, 30, 'all', True, 'Sweet milk dumplings in syrup'),
    ('Ice Cream', 'Dessert', 100, 'grams', 0.020, 5, 'summer', True, 'Assorted ice cream scoops'),
    ('Chocolate Brownie', 'Dessert', 70, 'grams', 0.025, 45, 'all', True, 'Rich chocolate brownie'),
    ('Fruit Salad', 'Dessert', 120, 'grams', 0.010, 15, 'summer', True, 'Fresh seasonal fruits'),
    ('Lemonade', 'Beverage', 250, 'ml', 0.004, 10, 'summer', True, 'Fresh squeezed lemonade'),
    ('Masala Chai', 'Beverage', 200, 'ml', 0.005, 10, 'winter', True, 'Spiced Indian tea'),
    ('Mango Lassi', 'Beverage', 250, 'ml', 0.006, 5, 'summer', True, 'Mango yogurt drink'),
    ('Soft Drinks', 'Beverage', 300, 'ml', 0.003, 2, 'all', True, 'Assorted soft drinks'),
    ('Caesar Salad', 'Salad', 100, 'grams', 0.012, 15, 'summer', True, 'Classic Caesar salad'),
    ('Greek Salad', 'Salad', 100, 'grams', 0.014, 10, 'summer', True, 'Fresh Mediterranean salad'),
    ('Steamed Rice', 'Bread & Rice', 150, 'grams', 0.004, 20, 'all', True, 'Plain steamed basmati rice'),
    ('Garlic Naan', 'Bread & Rice', 80, 'grams', 0.008, 15, 'all', True, 'Soft garlic flatbread'),
    ('Dinner Rolls', 'Bread & Rice', 60, 'grams', 0.007, 30, 'all', True, 'Soft dinner rolls'),
]


VENUES = [
    {
        'name': 'The Grand Palace',
        'city': 'Mumbai',
        'address': '12 Marine Drive, Mumbai',
        'contact': '+91 22 1234 5678',
        'dishes': ['Paneer Tikka', 'Butter Chicken', 'Biryani', 'Dal Makhani', 'Gulab Jamun',
                   'Garlic Naan', 'Steamed Rice', 'Masala Chai', 'Mango Lassi', 'Caesar Salad'],
    },
    {
        'name': 'Skyline Banquet',
        'city': 'Delhi',
        'address': '45 Connaught Place, Delhi',
        'contact': '+91 11 9876 5432',
        'dishes': ['Chicken Tikka', 'Palak Paneer', 'Grilled Fish', 'Pasta Arrabiata',
                   'Chocolate Brownie', 'Ice Cream', 'Lemonade', 'Soft Drinks',
                   'Greek Salad', 'Dinner Rolls'],
    },
    {
        'name': 'Garden View Resort',
        'city': 'Bangalore',
        'address': '8 MG Road, Bangalore',
        'contact': '+91 80 5555 1234',
        'dishes': ['Vegetable Spring Rolls', 'Soup of the Day', 'Bruschetta', 'Dal Makhani',
                   'Palak Paneer', 'Fruit Salad', 'Masala Chai', 'Lemonade',
                   'Caesar Salad', 'Garlic Naan', 'Steamed Rice'],
    },
]


class Command(BaseCommand):
    help = 'Seed initial categories and dishes'

    def handle(self, *args, **kwargs):
        # Create categories
        cat_map = {}
        for name, order in CATEGORIES:
            cat, _ = Category.objects.get_or_create(name=name, defaults={'order': order})
            cat_map[name] = cat

        # Create dishes
        created = 0
        for row in DISHES:
            name, cat_name, qty, unit, cost, prep, season, veg, desc = row
            _, made = Dish.objects.get_or_create(
                name=name,
                defaults=dict(
                    category=cat_map[cat_name],
                    quantity_per_person=qty,
                    unit=unit,
                    cost_per_unit=cost,
                    preparation_time=prep,
                    season=season,
                    is_vegetarian=veg,
                    description=desc,
                )
            )
            if made:
                created += 1

        self.stdout.write(self.style.SUCCESS(
            f'Seeded {len(CATEGORIES)} categories and {created} new dishes.'
        ))

        # Seed venues
        v_created = 0
        for vdata in VENUES:
            venue, made = Venue.objects.get_or_create(
                name=vdata['name'],
                defaults={'city': vdata['city'], 'address': vdata['address'], 'contact': vdata['contact']}
            )
            if made:
                v_created += 1
            for dish_name in vdata['dishes']:
                try:
                    dish = Dish.objects.get(name=dish_name)
                    VenueDish.objects.get_or_create(venue=venue, dish=dish)
                except Dish.DoesNotExist:
                    pass

        self.stdout.write(self.style.SUCCESS(
            f'Seeded {v_created} new venues with their menus.'
        ))
