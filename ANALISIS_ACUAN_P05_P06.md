# ANALISIS KETERKAITAN TUGAS P05 & P06 SEBAGAI ACUAN PROYEK AKHIR
**Mata Kuliah:** Sistem Cerdas (Semester 3)  
**Mahasiswa:** Ahmad Rifai  
**NIM:** 253307049  
**Institusi:** Politeknik Negeri Madiun  
**Proyek Akhir:** Sistem Pakar Diagnosa Risiko COVID-19 Berbasis Web (Django + Supabase + Tailwind CSS)  
**Tanggal Penyusunan:** November 2026  

---

## 1. RINGKASAN EKSEKUTIF

Dokumen ini menyajikan analisis komprehensif terhadap dua tugas laboratorium sebelumnya:
1. **Tugas P05 (Bab 4): Sistem Pakar Berbasis Aturan (Rule-Based Expert System)**
2. **Tugas P06 (Bab 5): Sistem Inferensi Logika Fuzzy (Fuzzy Inference System)**

Analisis ini memetakan bagaimana konsep teoretis, implementasi algoritma, serta eksperimen komputasi dari kedua tugas tersebut secara langsung diangkat, diadaptasi, dan disempurnakan menjadi arsitektur sistem pada **Proyek Akhir Sistem Pakar Diagnosa COVID-19**.

---

## 2. BEDAH MATERI P05 (SISTEM PAKAR) SEBAGAI FONDASI LOGIKA

Pada Tugas P05, fokus utama adalah pemisahan antara basis pengetahuan (*knowledge base*), memori kerja (*working memory*), dan mesin penalaran (*inference engine*).

### 2.1. Konsep Kunci P05 yang Diadopsi ke Proyek Akhir

| Komponen di P05 | Implementasi di P05 (Monitor PC & Laptop) | Implementasi di Proyek Akhir (COVID-19) |
|---|---|---|
| **Struktur Aturan JIKA-MAKA** | `{"jika": [...], "maka": "..."}` dalam Python List of Dict | Model `Aturan` Django (`diagnosa/models.py`) dan engine `ATURAN` (`knowledge/engine.py`) |
| **Hierarki Kesimpulan** | Memisahkan *kesimpulan antara* (`masalah_daya_monitor`) dan *diagnosa akhir* | Memisahkan kesimpulan antara (R01-R06: Demam, Batuk Intens, Rentan Usia) dan diagnosa akhir (R07: Risiko Tinggi, R08: Risiko Rendah) |
| **Forward Chaining (Bottom-Up)** | Looping `while ada_baru:` mengevaluasi fakta gejala hingga memori kerja stabil | Menjadi alur utama skrining pasien pada fungsi `forward_chaining(fakta)` di `knowledge/engine.py` |
| **Backward Chaining (Top-Down)** | Fungsi rekursif pembuktian hipotesis kerusakan komponen monitor | Diterapkan pada modul interaktif **Uji Dugaan** (`/uji-dugaan/`) untuk membuktikan target diagnosa secara deduktif |
| **Explanation Facility** | Pelacakan aturan terpicu yang dicetak pada output terminal | Tampilan visual **"Mengapa Hasil Ini Muncul?"** di halaman `/hasil/` yang menampilkan jejak penalaran transparan |

### 2.2. Landasan Etika Medis dari Esai 4 P05
Pada Esai 4 P05, dievaluasi kegagalan konsep *"sistem pakar segala penyakit"* karena melanggar syarat kelayakan domain sempit (*narrow domain*). Pelajaran ini menjadi dasar filosofis mengapa Proyek Akhir:
1. Mengkhususkan diri pada **skrining risiko COVID-19**, bukan diagnosis klinis umum.
2. Memasang **Medical Disclaimer** di setiap halaman untuk menegaskan bahwa sistem bersifat edukasi dan triase awal, bukan pengganti dokter.

---

## 3. BEDAH MATERI P06 (LOGIKA FUZZY) SEBAGAI ACUAN PENGEMBANGAN PARAMETER

Pada Tugas P06, fokus bergeser dari logika biner tegas (*crisp*) 0/1 menuju penalaran derajat keanggotaan $\mu(x) \in [0, 1]$ menggunakan inferensi Mamdani dan Sugeno.

### 3.1. Relevansi Konsep P06 terhadap Proyek Akhir

1. **Permasalahan Batas Tegas (*Threshold Dead-Zone*) pada Suhu:**
   * Di P06 Esai 4, dibuktikan bahwa membagi suhu tanpa *overlap* menciptakan titik mati (*dead-zone*).
   * Pada dataset COVID-19, parameter suhu tubuh pasien berada pada rentang numerik kontinu ($96.0^\circ\text{F} - 104.0^\circ\text{F}$ atau $35.6^\circ\text{C} - 40.0^\circ\text{C}$).
   * Proyek akhir menjembatani hal ini dengan menyediakan representasi linguistik:
     - Normal: $< 37.2^\circ\text{C}$
     - Hangat: $37.2^\circ\text{C} - 37.9^\circ\text{C}$
     - Demam: $\ge 38.0^\circ\text{C}$

2. **Kombinasi Gejala Multi-Variabel (Operator AND/OR):**
   * Di P06, dipelajari agregasi $\min$ untuk AND dan $\max$ untuk OR (seperti pada aturan kipas dan siram tanaman).
   * Di Proyek Akhir, aturan R05 (`Demam AND Batuk Intens`) dan R07 menggunakan penalaran konjungtif yang setara dengan evaluasi antecedent fuzzy sebelum mencapai kesimpulan tegas.

3. **Skor Keyakinan (*Confidence Score*):**
   * Diadaptasi dari konsep defuzzifikasi dan *Certainty Factor* (Esai 5 P06) untuk menghasilkan skor persentase keyakinan risiko (misal: 82% untuk Risiko Tinggi, 35% untuk Risiko Rendah).

---

## 4. MATRIKS PERBANDINGAN TIGA SISTEM

| Dimensi Evaluasi | Tugas P05 (Sistem Pakar) | Tugas P06 (Logika Fuzzy) | Proyek Akhir (Sistem Pakar COVID-19) |
|---|---|---|---|
| **Domain Masalah** | Kerusakan Hardware Monitor & Laptop | Kontrol Kecepatan Kipas & Siram Tanaman | Skrining Risiko Pasien COVID-19 |
| **Tipe Data Masukan** | Diskrit / String (`"layar_gelap"`, `"mati total"`) | Kontinu / Numerik (Suhu $0-45^\circ\text{C}$, Lembap $0-100\%$) | Campuran: Numerik Kontinu (Suhu, Usia) & Kategorikal (Batuk, Kota) |
| **Metode Inferensi** | Forward & Backward Chaining | Mamdani (Min-Max) & Defuzzifikasi Centroid | Forward & Backward Chaining berbasis Rule Engine |
| **Antarmuka (UI)** | Terminal CLI / Console Input | Grafik Matplotlib & Control Surface 3D | Web Modern Responsif (Django + Tailwind CSS + Chart.js) |
| **Manajemen Data** | List & Dict Memory (Volatile) | Array NumPy & DataFrame Pandas | Database Relasional Cloud Supabase (PostgreSQL 1.000+ Record) |
| **Fasilitas Penjelasan** | Teks jejak aturan terminal | Visualisasi agregasi grafik terpotong | Komponen UI Jejak Penalaran Berwarna dengan status Terpicu/Tidak |

---

## 5. REKOMENDASI PENGEMBANGAN LANJUTAN (NILAI PLUS UAS)

Berdasarkan sintesis keunggulan P05 dan P06, berikut adalah 3 peluang peningkatan teknis untuk kesempurnaan Proyek Akhir:

### Rekomendasi 1: Penambahan Modul Hibrida (Fuzzy-Expert System)
Mengintegrasikan algoritma fungsi trapesium/segitiga dari P06 (Cell 7 & 9) ke dalam validasi suhu tubuh pasien di Django:
- Pasien dengan suhu $37.9^\circ\text{C}$ tidak langsung divonis "Tidak Demam" secara kaku, melainkan memiliki derajat $\mu_{\text{hangat}} = 0.8$ dan $\mu_{\text{demam}} = 0.2$. Hal ini akan membuat skor keyakinan risiko menjadi dinamis matematis.

### Rekomendasi 2: Dokumentasi Arsitektur untuk Presentasi Dosen
Dalam slide presentasi UAS, sajikan diagram pohon penalaran dari P05 bersanding dengan diagram pie-chart dan visualisasi data yang ada pada web dashboard saat ini. Ini membuktikan kesinambungan belajar dari P01 hingga P14.

---
*Dokumen ini disusun secara otomatis oleh Asisten Coding Antigravity sebagai referensi ilmiah laporan proyek akhir.*
