from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='landing.html'), name='landing'),
    path('login/', TemplateView.as_view(template_name='login.html'), name='login'),
    path('register/', TemplateView.as_view(template_name='register.html'), name='register'),
    path('dashboard/', TemplateView.as_view(template_name='dashboard.html'), name='dashboard'),
    path('events/create/', TemplateView.as_view(template_name='create_event.html'), name='create_event'),
    path('events/<int:event_id>/menu/', TemplateView.as_view(template_name='menu_selection.html'), name='menu_selection'),
    path('events/<int:event_id>/result/', TemplateView.as_view(template_name='buffet_result.html'), name='buffet_result'),
    path('analytics/', TemplateView.as_view(template_name='analytics.html'), name='analytics'),
    path('admin-panel/', TemplateView.as_view(template_name='admin_panel.html'), name='admin_panel'),
    path('profile/', TemplateView.as_view(template_name='profile.html'), name='profile'),
]
