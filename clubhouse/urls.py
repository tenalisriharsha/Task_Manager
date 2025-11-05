# File: clubhouse/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),  # keep Django admin for superuser power use
    path('', include('tasksapp.urls', namespace='tasksapp')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('elections/', include('elections.urls', namespace='elections')),
    path('core/', include('core.urls', namespace='core')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
