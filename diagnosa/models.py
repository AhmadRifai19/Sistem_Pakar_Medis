# diagnosa/models.py
from django.db import models


class Gejala(models.Model):
    kode = models.CharField(max_length=10, unique=True)
    nama = models.CharField(max_length=100)
    deskripsi = models.TextField(blank=True)

    def __str__(self):
        return f"{self.kode}: {self.nama}"


class Aturan(models.Model):
    JENIS_CHOICES = [
        ('antara', 'Kesimpulan Antara'),
        ('akhir', 'Diagnosa Akhir'),
    ]

    kode = models.CharField(max_length=10, unique=True)
    kondisi = models.TextField()
    kesimpulan = models.CharField(max_length=200)
    jenis = models.CharField(max_length=10, choices=JENIS_CHOICES, default='antara')
    urutan = models.IntegerField(default=0)

    class Meta:
        ordering = ['urutan']

    def __str__(self):
        return f"{self.kode}: JIKA {self.kondisi} MAKA {self.kesimpulan}"


class Konsultasi(models.Model):
    nama = models.CharField(max_length=100, blank=True)
    usia = models.IntegerField()
    gender = models.CharField(max_length=20)
    fever = models.FloatField()
    cough = models.CharField(max_length=20)
    city = models.CharField(max_length=50)
    risiko = models.CharField(max_length=20)
    keyakinan = models.IntegerField(default=0)
    aturan_terpicu = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def fever_c(self):
        return round((self.fever - 32) * 5 / 9, 1)

    def __str__(self):
        return f"{self.nama or 'Anonim'} - {self.risiko} ({self.created_at:%Y-%m-%d})"
