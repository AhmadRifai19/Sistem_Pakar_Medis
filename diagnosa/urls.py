# diagnosa/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.beranda, name='beranda'),
    path('konsultasi/', views.konsultasi, name='konsultasi'),
    path('hasil/', views.hasil, name='hasil'),
    path('basis-pengetahuan/', views.basis_pengetahuan, name='basis_pengetahuan'),
    path('uji-dugaan/', views.uji_dugaan, name='uji_dugaan'),
    path('statistik/', views.statistik, name='statistik'),
    path('dataset/', views.dataset, name='dataset'),
    path('tim/', views.tim, name='tim'),
    # URL baru untuk grafik transisi halus
    path('grafik_transisi_suhu/', views.grafik_transisi_suhu, name='grafik_transisi_suhu'),
]
