"""
URL configuration for Sistem Pakar Medis COVID-19.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('diagnosa.urls')),
]
