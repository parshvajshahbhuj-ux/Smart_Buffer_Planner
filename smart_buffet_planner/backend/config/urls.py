from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/events/', include('events.urls')),
    path('api/menu/', include('menu.urls')),
    path('api/analytics/', include('analytics.urls')),
    path('api/reports/', include('reports.urls')),
    # Frontend views
    path('', include('accounts.frontend_urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
