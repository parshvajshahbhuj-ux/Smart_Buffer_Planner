from django.urls import path
from .views import EventReportView

urlpatterns = [
    path('event/<int:event_id>/pdf/', EventReportView.as_view(), name='event_report'),
]
