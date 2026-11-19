# Proyek_Sistem_Cerdas/core/urls.py (tambahkan ini ke urls utama proyek)
"""
Tambahkan baris berikut ke `core/urls.py`:

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('diagnosa.urls')),
]
"""
