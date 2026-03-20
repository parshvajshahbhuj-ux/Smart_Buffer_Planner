from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, DishViewSet, VenueViewSet

router = DefaultRouter()
router.register('categories', CategoryViewSet)
router.register('dishes', DishViewSet)
router.register('venues', VenueViewSet)

urlpatterns = [path('', include(router.urls))]
