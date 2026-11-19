# diagnosa/views.py
from django.shortcuts import render, redirect
from django.db.models import Count, Avg
from knowledge.engine import forward_chaining, tentukan_risiko, backward_chaining, ATURAN
from knowledge.ai_explainer import jelaskan_perbandingan_fuzzy_crisp


def beranda(request):
    return render(request, 'beranda.html')


def konsultasi(request):
    from diagnosa.models import Konsultasi
    kota_list = list(Konsultasi.objects.values_list('city', flat=True).distinct().order_by('city'))
    if not kota_list:
        kota_list = ['Bangalore', 'Delhi', 'Kolkata', 'Mumbai']
    return render(request, 'konsultasi.html', {'daftar_kota': kota_list})


def hasil(request):
    if request.method != 'POST':
        return redirect('konsultasi')

    nama = request.POST.get('nama', '').strip()
    usia = int(request.POST.get('usia', 24))
    gender = request.POST.get('gender', 'Perempuan')
    fever = float(request.POST.get('fever', 101.2))
    cough = request.POST.get('cough', 'Strong')
    
    city = request.POST.get('city', 'Mumbai').strip()
    custom_city = request.POST.get('custom_city', '').strip()
    if city == 'other' and custom_city:
        city = custom_city.strip().title()
    elif city == 'other':
        city = 'Lainnya'

    fakta = {
        'usia': usia,
        'gender': gender,
        'fever': fever,
        'cough': cough,
        'city': city,
    }

    # Simpan ke database
    from diagnosa.models import Konsultasi
    aturan_hasil = forward_chaining(fakta)
    risiko, keyakinan, alasan = tentukan_risiko(fakta, aturan_hasil)
    terpicu_count = sum(1 for a in aturan_hasil if a['terpicu'])
    terpicu_str = ", ".join([a["kode"] for a in aturan_hasil if a["terpicu"]])

    Konsultasi.objects.create(
        nama=nama or 'Anonim',
        usia=usia,
        gender=gender,
        fever=fever,
        cough=cough,
        city=city,
        risiko=risiko,
        keyakinan=keyakinan,
        aturan_terpicu=terpicu_str,
    )

    if risiko == 'Tinggi':
        saran = [
            {'nomor': '01', 'judul': 'Batasi kontak', 'deskripsi': 'Kurangi kontak dengan orang lain dan gunakan masker.'},
            {'nomor': '02', 'judul': 'Hubungi tenaga kesehatan', 'deskripsi': 'Konsultasikan gejala dan kebutuhan pemeriksaan lebih lanjut.'},
            {'nomor': '03', 'judul': 'Pantau kondisi Anda', 'deskripsi': 'Catat suhu dan perubahan gejala secara berkala.'},
        ]
    elif risiko == 'Rendah':
        saran = [
            {'nomor': '01', 'judul': 'Istirahat cukup', 'deskripsi': 'Jaga daya tahan tubuh dengan istirahat dan nutrisi yang baik.'},
            {'nomor': '02', 'judul': 'Pantau suhu', 'deskripsi': 'Jika suhu meningkat atau gejala memburuk, lakukan skrining ulang.'},
            {'nomor': '03', 'judul': 'Terapkan prokes', 'deskripsi': 'Tetap jaga kebersihan tangan dan etika batuk.'},
        ]
    else:
        saran = [
            {'nomor': '01', 'judul': 'Waspada & Pantau', 'deskripsi': 'Pantau perkembangan gejala secara rutin dalam 3–5 hari ke depan.'},
            {'nomor': '02', 'judul': 'Konsultasi awal', 'deskripsi': 'Hubungi puskesmas atau klinik terdekat jika gejala memburuk.'},
            {'nomor': '03', 'judul': 'Terapkan prokes', 'deskripsi': 'Gunakan masker dan jaga jarak untuk mencegah penularan.'},
        ]

    context = {
        'hasil': {
            'nama': nama,
            'usia': usia,
            'gender': gender,
            'fever': fever,
            'fever_c': round((fever - 32) * 5 / 9, 1),
            'cough': 'Kuat' if cough == 'Strong' else 'Ringan',
            'city': city,
            'risiko': risiko,
            'keyakinan': keyakinan,
            'alasan': alasan,
            'aturan': aturan_hasil,
            'jumlah_terpicu': terpicu_count,
            'total_aturan': len(aturan_hasil),
            'saran': saran,
        },
        'penjelasan_transisi': jelaskan_perbandingan_fuzzy_crisp(),
        'fever_user_f': fever,
        'fever_user_c': round((fever - 32) * 5 / 9, 1),
    }
    return render(request, 'hasil.html', context)


def basis_pengetahuan(request):
    aturan_list = [
        {
            'kode': a['kode'],
            'kondisi': a['kondisi'],
            'kesimpulan': a['kesimpulan'],
            'jenis': 'Diagnosa Akhir' if a['jenis'] == 'akhir' else 'Kesimpulan Antara'
        }
        for a in ATURAN
    ]
    return render(request, 'basis_pengetahuan.html', {'aturan_list': aturan_list})


def uji_dugaan(request):
    hasil_uji = None
    if request.method == 'POST':
        dugaan = request.POST.get('dugaan', 'risiko_tinggi')
        fakta = request.POST.getlist('fakta')
        hasil_uji = backward_chaining(dugaan, set(fakta))

    return render(request, 'uji_dugaan.html', {'hasil_uji': hasil_uji})


def grafik_transisi_suhu(request):
    return render(request, 'grafik_suhu_chart.html')


def statistik(request):
    from diagnosa.models import Konsultasi
    from django.db.models import Count, Avg
    from knowledge.ai_explainer import jelaskan_statistik_grafik

    total = Konsultasi.objects.count()
    avg_suhu_f = Konsultasi.objects.aggregate(Avg('fever'))['fever__avg'] or 0
    avg_suhu_c = round((avg_suhu_f - 32) * 5 / 9, 1) if avg_suhu_f else 0

    # Distribusi per kota dari DB
    kota_data = (
        Konsultasi.objects
        .values('city')
        .annotate(jumlah=Count('id'))
        .order_by('-jumlah')[:6]
    )
    max_kota = max((k['jumlah'] for k in kota_data), default=1)
    distribusi_kota = [
        {
            'nama': k['city'],
            'jumlah': k['jumlah'],
            'persen': round(k['jumlah'] / total * 100) if total > 0 else 0,
        }
        for k in kota_data
    ]

    # Distribusi risiko dari DB
    risiko_data = Konsultasi.objects.values('risiko').annotate(jumlah=Count('id'))
    distribusi_risiko = {r['risiko']: r['jumlah'] for r in risiko_data}

    tinggi = distribusi_risiko.get('Tinggi', 0)
    sedang = distribusi_risiko.get('Sedang', 0)
    rendah = distribusi_risiko.get('Rendah', 0)

    p_tinggi = round(tinggi / total * 100) if total > 0 else 0
    p_sedang = round(sedang / total * 100) if total > 0 else 0
    p_rendah = round(rendah / total * 100) if total > 0 else 0

    # Penjelasan Otomatis Berbasis AI Groq (seperti di Tugas P06)
    penjelasan_ai = jelaskan_statistik_grafik(
        total_pasien=total,
        tinggi=tinggi,
        sedang=sedang,
        rendah=rendah,
        p_tinggi=p_tinggi,
        p_sedang=p_sedang,
        p_rendah=p_rendah,
        avg_suhu_c=avg_suhu_c,
        kota_list=distribusi_kota,
        fever_user_c=avg_suhu_c
    )

    context = {
        'total_pasien': total,
        'rata_suhu': round(avg_suhu_f, 1),
        'rata_suhu_c': avg_suhu_c,
        'jumlah_tinggi': tinggi,
        'jumlah_sedang': sedang,
        'jumlah_rendah': rendah,
        'persen_tinggi': p_tinggi,
        'persen_sedang': p_sedang,
        'persen_rendah': p_rendah,
        'distribusi_kota': distribusi_kota,
        'penjelasan_ai': penjelasan_ai,
    }
    return render(request, 'statistik.html', context)


def dataset(request):
    from diagnosa.models import Konsultasi
    from django.core.paginator import Paginator

    qs = Konsultasi.objects.all().order_by('id')
    paginator = Paginator(qs, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    return render(request, 'dataset.html', {'page_obj': page_obj, 'total': qs.count()})


def tim(request):
    return render(request, 'tim.html')
