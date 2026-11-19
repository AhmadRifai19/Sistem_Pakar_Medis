# knowledge/engine.py
"""
Mesin inferensi sistem pakar diagnosa COVID-19.
Mengadaptasi logika forward chaining dan backward chaining dari Tugas P05.
"""

ATURAN = [
    {
        "kode": "R01",
        "kondisi": "Suhu ≥ 38.0 °C (100.4 °F)",
        "kesimpulan": "Demam",
        "jenis": "antara",
        "cek": lambda f: f["fever"] >= 100.4,
    },
    {
        "kode": "R02",
        "kondisi": "Suhu < 38.0 °C (100.4 °F)",
        "kesimpulan": "Tidak Demam",
        "jenis": "antara",
        "cek": lambda f: f["fever"] < 100.4,
    },
    {
        "kode": "R03",
        "kondisi": "Batuk = Kuat",
        "kesimpulan": "Batuk Intens",
        "jenis": "antara",
        "cek": lambda f: f["cough"] == "Strong",
    },
    {
        "kode": "R04",
        "kondisi": "Batuk = Ringan",
        "kesimpulan": "Batuk Ringan",
        "jenis": "antara",
        "cek": lambda f: f["cough"] == "Mild",
    },
    {
        "kode": "R05",
        "kondisi": "Demam DAN Batuk Intens",
        "kesimpulan": "Kombinasi Gejala Utama",
        "jenis": "antara",
        "cek": lambda f: f["fever"] >= 100.4 and f["cough"] == "Strong",
    },
    {
        "kode": "R06",
        "kondisi": "Usia ≥ 60 tahun",
        "kesimpulan": "Rentan Usia",
        "jenis": "antara",
        "cek": lambda f: f["usia"] >= 60,
    },
    {
        "kode": "R07",
        "kondisi": "Kombinasi Gejala Utama",
        "kesimpulan": "Risiko Tinggi — Indikasi COVID-19",
        "jenis": "akhir",
        "cek": lambda f: f["fever"] >= 100.4 and f["cough"] == "Strong",
    },
    {
        "kode": "R08",
        "kondisi": "Tidak Demam DAN Batuk Ringan",
        "kesimpulan": "Risiko Rendah",
        "jenis": "akhir",
        "cek": lambda f: f["fever"] < 100.4 and f["cough"] == "Mild",
    },
]


def forward_chaining(fakta):
    """
    Jalankan forward chaining.
    fakta: dict dengan key 'usia', 'fever', 'cough', 'gender', 'city'
    Mengembalikan list aturan beserta status terpicu.
    """
    hasil = []
    for aturan in ATURAN:
        terpicu = aturan["cek"](fakta)
        hasil.append({
            "kode": aturan["kode"],
            "kondisi": aturan["kondisi"],
            "kesimpulan": aturan["kesimpulan"],
            "jenis": aturan["jenis"],
            "terpicu": terpicu,
        })
    return hasil


def trapesium(x, a, b, c, d):
    """Fungsi keanggotaan trapesium sesuai Tugas P06."""
    if x <= a or x >= d:
        return 0.0
    if a < x <= b:
        return (x - a) / (b - a)
    if b < x <= c:
        return 1.0
    return (d - x) / (d - c)


def hitung_skor_fuzzy(fakta):
    """
    Menghitung skor keyakinan menggunakan logika fuzzy dari P06.
    Output: Nilai keyakinan 0-100.
    """
    suhu_f = fakta['fever']
    usia = fakta['usia']
    batuk = fakta['cough']

    # 1. Fuzzifikasi Suhu (°F)
    # Dingin/Normal: 96-99, luruh ke 100.4
    mu_normal = trapesium(suhu_f, 90, 96, 99, 100.4)
    # Demam: naik dari 99, penuh di 100.4 ke atas
    mu_demam = trapesium(suhu_f, 99, 100.4, 110, 110)

    # 2. Fuzzifikasi Batuk (Kategorikal as Fuzzy)
    mu_batuk_kuat = 1.0 if batuk == "Strong" else 0.0
    mu_batuk_ringan = 1.0 if batuk == "Mild" else 0.0

    # 3. Fuzzifikasi Usia (Rentan)
    # Rentan: mulai naik dari usia 50, penuh di 60
    mu_rentan = trapesium(usia, 50, 60, 150, 150)

    # 4. Evaluasi Aturan (Mamdani Min-Max dari P06)
    # Aturan Risiko Tinggi (R07): Demam AND Batuk Intens
    w_tinggi = min(mu_demam, mu_batuk_kuat)
    
    # Aturan Risiko Rendah (R08): Normal AND Batuk Ringan
    w_rendah = min(mu_normal, mu_batuk_ringan)

    # 5. Defuzzifikasi Sederhana (Weighted Average ala Sugeno P06)
    # Konstanta target: Tinggi=90, Sedang=50, Rendah=20
    # Jika tidak ada yang dominan, default ke Sedang
    if w_tinggi > 0:
        skor = 70 + (w_tinggi * 25) + (mu_rentan * 5) # 70-100
    elif w_rendah > 0:
        skor = 10 + (w_rendah * 25) # 10-35
    else:
        # Zona Sedang (di antara keduanya atau overlap)
        skor = 40 + (mu_demam * 15) + (mu_rentan * 10)

    return round(min(max(skor, 0), 100))


def tentukan_risiko(fakta, aturan_hasil):
    """Tentukan risiko akhir berdasarkan aturan terpicu dan skor fuzzy."""
    terpicu = [a for a in aturan_hasil if a["terpicu"]]
    ada_r07 = any(a["kode"] == "R07" and a["terpicu"] for a in aturan_hasil)
    ada_r08 = any(a["kode"] == "R08" and a["terpicu"] for a in aturan_hasil)

    # Hitung skor menggunakan mesin fuzzy P06
    keyakinan = hitung_skor_fuzzy(fakta)

    if ada_r07:
        return "Tinggi", keyakinan, "Kombinasi gejala utama (Demam & Batuk Kuat) terdeteksi. Sistem mengidentifikasi indikasi risiko tinggi COVID-19."
    elif ada_r08:
        return "Rendah", keyakinan, "Gejala yang dialami cenderung ringan dan suhu tubuh dalam batas normal. Risiko tergolong rendah."
    else:
        return "Sedang", keyakinan, f"{len(terpicu)} aturan terpicu. Kondisi menunjukkan gejala yang perlu dipantau meskipun tidak memenuhi kriteria risiko tinggi secara penuh."


def backward_chaining(dugaan, fakta_user):
    """
    Jalankan backward chaining untuk membuktikan dugaan.
    dugaan: 'risiko_tinggi' atau 'risiko_rendah'
    fakta_user: set of string ('demam', 'batuk_kuat', 'batuk_ringan', 'lansia')
    """
    pohon = []

    if dugaan == "risiko_tinggi":
        butuh_demam = "demam" in fakta_user
        butuh_batuk = "batuk_kuat" in fakta_user

        pohon.append({"level": 0, "nama": "RISIKO TINGGI (R07)", "keterangan": "Butuh: Kombinasi Gejala Utama", "terbukti": butuh_demam and butuh_batuk})
        pohon.append({"level": 1, "nama": "Kombinasi Gejala Utama (R05)", "keterangan": "Butuh: Demam DAN Batuk Intens", "terbukti": butuh_demam and butuh_batuk})
        pohon.append({"level": 2, "nama": "Demam (R01)", "keterangan": "Butuh: Suhu ≥ 100.4 °F", "terbukti": butuh_demam})
        pohon.append({"level": 2, "nama": "Batuk Intens (R03)", "keterangan": "Butuh: Batuk = Kuat", "terbukti": butuh_batuk})

        terbukti = butuh_demam and butuh_batuk
        kesimpulan = "Dugaan TERBUKTI. Kedua kondisi R05 terpenuhi." if terbukti else "Dugaan TIDAK TERBUKTI. Salah satu atau kedua kondisi tidak terpenuhi."

    else:
        tidak_demam = "demam" not in fakta_user
        batuk_ringan = "batuk_ringan" in fakta_user

        pohon.append({"level": 0, "nama": "RISIKO RENDAH (R08)", "keterangan": "Butuh: Tidak Demam DAN Batuk Ringan", "terbukti": tidak_demam and batuk_ringan})
        pohon.append({"level": 1, "nama": "Tidak Demam (R02)", "keterangan": "Butuh: Suhu < 100.4 °F", "terbukti": tidak_demam})
        pohon.append({"level": 1, "nama": "Batuk Ringan (R04)", "keterangan": "Butuh: Batuk = Ringan", "terbukti": batuk_ringan})

        terbukti = tidak_demam and batuk_ringan
        kesimpulan = "Dugaan TERBUKTI. Kedua kondisi R08 terpenuhi." if terbukti else "Dugaan TIDAK TERBUKTI. Salah satu atau kedua kondisi tidak terpenuhi."

    return {"terbukti": terbukti, "pohon": pohon, "kesimpulan": kesimpulan, "dugaan": dugaan}
