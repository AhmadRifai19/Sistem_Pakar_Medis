# knowledge/ai_explainer.py
"""
Modul Penjelasan Grafik Menggunakan AI Groq
Diadaptasi dari kode pengembangan Tugas P06 (Bab 5 Logika Fuzzy).
Menggunakan model qwen/qwen3.8-27b atau llama-3.3-70b-versatile via Groq API.
"""

import os
from django.core.cache import cache

def jelaskan_statistik_grafik(total_pasien, tinggi, sedang, rendah, p_tinggi, p_sedang, p_rendah, avg_suhu_c, kota_list, fever_user_c=None):
    """
    Menghasilkan narasi ilmiah dari data grafik statistik menggunakan Groq API.
    Dilengkapi sistem fallback cerdas jika API key belum diset.
    """
    cache_key = f"groq_stat_{total_pasien}_{tinggi}_{sedang}_{rendah}_{fever_user_c or 'default'}"
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result

    groq_api_key = os.getenv("GROQ_API_KEY")

    # Jika Groq API key tersedia, panggil model Groq seperti di P06
    if groq_api_key:
        try:
            from groq import Groq
            client = Groq(api_key=groq_api_key)

            nama_kota_terbanyak = [f"{k['nama']} ({k['jumlah']} pasien)" for k in kota_list[:3]]
            kota_str = ", ".join(nama_kota_terbanyak) if nama_kota_terbanyak else "berbagai kota"

            fever_note = ""
            if fever_user_c is not None:
                fever_note = f"\n- Suhu pasien uji eksperimental: {fever_user_c}°C.\n- Normal: <37.2°C, Hangat: 37.2–37.9°C, Demam: ≥38.0°C. Pasien berada pada kategori {('Demam' if fever_user_c >= 38.0 else 'Hangat/Normal')}."

            prompt_sistem = (
                f"Data Statistik Skrining Risiko COVID-19 ({total_pasien} Pasien):\n"
                f"- Proporsi Risiko (Pie Chart): Tinggi {p_tinggi}% ({tinggi} orang), Sedang {p_sedang}% ({sedang} orang), Rendah {p_rendah}% ({rendah} orang).\n"
                f"- Rata-rata suhu tubuh pasien: {avg_suhu_c}°C.\n"
                f"- Distribusi kasus per kota terbanyak: {kota_str}.\n"
                f"- Model inferensi: Forward Chaining berbasis aturan gejala dan fungsi trapesium fuzzy.{fever_note}\n\n"
                f"Jawablah dengan 2 paragraf rapi yang mengalir (tanpa bullet/poin/numbering), bahasa Indonesia formal ilmiah seperti format laporan praktikum sistem cerdas. "
                f"Paragraf 1: Jelaskan interpretasi distribusi proporsi risiko pada diagram lingkaran dan signifikansi kasus risiko tinggi. "
                f"Paragraf 2: Analisis korelasi rata-rata suhu pasien dengan sebaran wilayah perkotaan serta implikasinya terhadap triase medis preventif."
            )

            # Memakai model yang sama persis dengan P06 (qwen/qwen-2.5-32b atau llama-3.3-70b-versatile)
            model_name = "llama-3.3-70b-versatile"
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt_sistem}],
                model=model_name,
                max_tokens=400,
                temperature=0.3
            )
            penjelasan = chat_completion.choices[0].message.content
            cache.set(cache_key, penjelasan, timeout=3600) # Cache 1 jam
            return penjelasan
        except Exception as e:
            pass

    # Narasi Fallback Ilmiah (bergaya evaluasi sistem cerdas P06)
    nama_kota = [k['nama'] for k in kota_list[:3]]
    kota_text = ", ".join(nama_kota) if nama_kota else "wilayah urban"
    
    penjelasan_default = (
        f"Berdasarkan visualisasi diagram lingkaran proporsi tingkat risiko terhadap {total_pasien} sampel data pasien, "
        f"terlihat bahwa kategori risiko tinggi mencakup {p_tinggi}% ({tinggi} pasien), risiko sedang sebesar {p_sedang}% ({sedang} orang), "
        f"dan risiko rendah sebesar {p_rendah}% ({rendah} orang). Dominansi proporsi risiko tinggi dan sedang merefleksikan sensitivitas "
        f"mesin inferensi aturan berantai dalam mendeteksi kombinasi gejala demam intensif dan batuk kuat, sehingga mampu memfilter "
        f"pasien yang membutuhkan perhatian medis prioritas secara efektif dan transparan.\n\n"
        f"Ditinjau dari parameter fisiologis dan demografi, rata-rata suhu tubuh pasien tercatat sebesar {avg_suhu_c}°C "
        f"dengan konsentrasi sebaran tertinggi berada di kota {kota_text}. Korelasi antara suhu di atas ambang batas normal (≥ 38.0°C) "
        f"dengan kepadatan populasi di kawasan perkotaan tersebut menggarisbawahi urgensi pemantauan preventif berkelanjutan. "
        f"Implementasi penalaran berbasis aturan yang dipadukan dengan pemetaan data spasial ini memberikan nilai strategis bagi "
        f"pengambilan keputusan triase klinis awal yang terukur dan objektif."
    )
    return penjelasan_default


def jelaskan_perbandingan_fuzzy_crisp():
    """
    Menghasilkan narasi AI Groq untuk menjelaskan perbedaan Logika Fuzzy vs Crisp 
    pada grafik transisi suhu tubuh (Tugas P06).
    """
    cache_key = "groq_fuzzy_crisp_explanation"
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result

    groq_api_key = os.getenv("GROQ_API_KEY")

    if groq_api_key:
        try:
            from groq import Groq
            client = Groq(api_key=groq_api_key)

            prompt_sistem = (
                "Jelaskan perbedaan antara Logika Fuzzy (halus) dan Logika Crisp (tegas/kaku) dalam konteks "
                "skrining suhu tubuh medis (Ambang batas 38.0°C). "
                "Gunakan gaya bahasa laporan praktikum sistem cerdas yang formal dan ilmiah dalam Bahasa Indonesia. "
                "Jelaskan mengapa transisi halus (Fuzzy) lebih unggul daripada cut-off kaku (Crisp) dalam mendeteksi "
                "risiko klinis yang tidak pasti. "
                "Tulis dalam 2 paragraf padat (maksimal 150 kata)."
            )

            model_name = "llama-3.3-70b-versatile"
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt_sistem}],
                model=model_name,
                max_tokens=300,
                temperature=0.3
            )
            penjelasan = chat_completion.choices[0].message.content
            cache.set(cache_key, penjelasan, timeout=86400) # Cache 24 jam
            return penjelasan
        except Exception:
            pass

    # Fallback jika API bermasalah
    return (
        "Grafik di atas memvisualisasikan perbedaan fundamental antara pendekatan logika tegas (Crisp) dan logika samar (Fuzzy). "
        "Logika Crisp menggunakan ambang batas kaku (threshold) di mana suhu di bawah 38.0°C dianggap nol mutlak, sedangkan tepat 38.0°C "
        "dianggap sebagai kondisi 'panas' sepenuhnya. Pendekatan ini kurang akurat dalam konteks medis karena mengabaikan ambiguitas data "
        "di sekitar ambang batas kritis.\n\n"
        "Sebaliknya, kurva Logika Fuzzy menunjukkan transisi gradual yang direpresentasikan oleh fungsi keanggotaan trapesium. "
        "Hal ini memungkinkan sistem untuk memberikan derajat keyakinan yang proporsional, sehingga suhu 37.9°C tetap memiliki bobot "
        "risiko tertentu alih-alih diabaikan. Keunggulan ini memberikan kehalusan reaksi (smoothness) pada mesin inferensi, "
        "memungkinkan keputusan klinis yang lebih presisi dan objektif dalam menangani ketidakpastian data biologis pasien."
    )
