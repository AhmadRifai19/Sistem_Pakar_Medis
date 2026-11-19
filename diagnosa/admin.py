from django.contrib import admin
from .models import Gejala, Aturan, Konsultasi

@admin.register(Gejala)
class GejalaAdmin(admin.ModelAdmin):
    list_display = ('kode', 'nama', 'deskripsi')
    search_fields = ('kode', 'nama')

@admin.register(Aturan)
class AturanAdmin(admin.ModelAdmin):
    list_display = ('kode', 'kondisi', 'kesimpulan', 'jenis', 'urutan')
    list_filter = ('jenis',)
    ordering = ('urutan',)

@admin.register(Konsultasi)
class KonsultasiAdmin(admin.ModelAdmin):
    list_display = ('id', 'nama', 'usia', 'gender', 'fever', 'cough', 'city', 'risiko', 'keyakinan', 'created_at')
    list_filter = ('risiko', 'city', 'gender')
    search_fields = ('nama', 'city')
    readonly_fields = ('created_at',)
