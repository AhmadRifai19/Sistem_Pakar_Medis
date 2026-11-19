import csv
from pathlib import Path
from django.core.management.base import BaseCommand
from diagnosa.models import Konsultasi, Aturan, Gejala
from knowledge.engine import forward_chaining, tentukan_risiko, ATURAN

GEJALA_AWAL = [
    {"kode": "G01", "nama": "Demam (Fever ≥ 100.4 °F)", "deskripsi": "Suhu tubuh meningkat melampaui batas normal (38°C / 100.4°F)."},
    {"kode": "G02", "nama": "Suhu Normal / Rendah (< 100.4 °F)", "deskripsi": "Suhu tubuh berada dalam rentang normal."},
    {"kode": "G03", "nama": "Batuk Kuat (Strong Cough)", "deskripsi": "Batuk dengan intensitas tinggi, terus menerus, atau kering parah."},
    {"kode": "G04", "nama": "Batuk Ringan (Mild Cough)", "deskripsi": "Batuk sesekali dengan intensitas rendah."},
    {"kode": "G05", "nama": "Usia Lanjut (≥ 60 tahun)", "deskripsi": "Faktor kerentanan usia lanjut dengan imunitas lebih rendah."},
    {"kode": "G06", "nama": "Riwayat Kontak / Wilayah Endemis", "deskripsi": "Tinggal atau bepergian ke zona kota dengan kasus COVID-19 tinggi."},
]

class Command(BaseCommand):
    help = 'Inisialisasi Gejala, Aturan, dan Impor Dataset COVID-19 (1000 record)'

    def add_arguments(self, parser):
        parser.add_argument('--csv', type=str, default='dataset_covid.csv', help='Path ke file CSV')

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("1. Menginisialisasi Basis Data Gejala..."))
        for g in GEJALA_AWAL:
            obj, created = Gejala.objects.get_or_create(
                kode=g["kode"],
                defaults={"nama": g["nama"], "deskripsi": g["deskripsi"]}
            )
            if created:
                self.stdout.write(f"  + Gejala {g['kode']} ditambahkan.")

        self.stdout.write(self.style.NOTICE("\n2. Menginisialisasi Basis Data Aturan (P05)..."))
        for i, a in enumerate(ATURAN, start=1):
            obj, created = Aturan.objects.get_or_create(
                kode=a["kode"],
                defaults={
                    "kondisi": a["kondisi"],
                    "kesimpulan": a["kesimpulan"],
                    "jenis": a["jenis"],
                    "urutan": i
                }
            )
            if created:
                self.stdout.write(f"  + Aturan {a['kode']} ditambahkan.")

        csv_path = Path(options['csv'])
        if not csv_path.exists():
            csv_path = Path(__file__).resolve().parent.parent.parent.parent / options['csv']

        if not csv_path.exists():
            self.stdout.write(self.style.ERROR(f"File CSV {options['csv']} tidak ditemukan!"))
            return

        self.stdout.write(self.style.NOTICE(f"\n3. Membaca & Mengimpor {csv_path}..."))
        
        count_existing = Konsultasi.objects.count()
        if count_existing >= 1000:
            self.stdout.write(self.style.WARNING(f"Database sudah berisi {count_existing} record. Melewati impor ulang."))
            return

        objects_to_create = []
        with open(csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # Kolom: Age,Gender,Fever,Cough,City,Has_Covid
            for idx, row in enumerate(reader, start=1):
                try:
                    usia = int(float(row.get('Age', 0)))
                    gender = row.get('Gender', 'Unknown').strip()
                    fever = float(row.get('Fever', 98.6))
                    cough = row.get('Cough', 'Mild').strip()
                    city = row.get('City', 'Unknown').strip()

                    fakta = {
                        'usia': usia,
                        'gender': gender,
                        'fever': fever,
                        'cough': cough,
                        'city': city,
                    }
                    aturan_hasil = forward_chaining(fakta)
                    risiko, keyakinan, _ = tentukan_risiko(fakta, aturan_hasil)
                    terpicu_str = ", ".join([a["kode"] for a in aturan_hasil if a["terpicu"]])

                    obj = Konsultasi(
                        nama=f"Pasien #{idx:04d}",
                        usia=usia,
                        gender=gender,
                        fever=fever,
                        cough=cough,
                        city=city,
                        risiko=risiko,
                        keyakinan=keyakinan,
                        aturan_terpicu=terpicu_str,
                    )
                    objects_to_create.append(obj)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error baris {idx}: {e}"))

        Konsultasi.objects.bulk_create(objects_to_create, batch_size=500)
        self.stdout.write(self.style.SUCCESS(f"BERHASIL! {len(objects_to_create)} record dataset berhasil diimpor ke database."))
