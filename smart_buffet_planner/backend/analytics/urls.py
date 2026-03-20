from django.urls import path
from .views import DashboardAnalyticsView, EventAnalyticsView, PredictionView

urlpatterns = [
    path('dashboard/', DashboardAnalyticsView.as_view(), name='dashboard_analytics'),
    path('event/<int:event_id>/', EventAnalyticsView.as_view(), name='event_analytics'),
    path('predict/', PredictionView.as_view(), name='predict'),
]
