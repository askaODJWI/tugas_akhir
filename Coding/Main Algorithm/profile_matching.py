# -*- coding: utf-8 -*-
"""
Skrip Python untuk Sistem Pendukung Keputusan (SPK)
menggunakan metode Profile Matching guna menentukan persona user
untuk rekomendasi properti.
"""

# ---------------------------------------------------------------------------
# BAGIAN 1: KONFIGURASI DATA (ISI DENGAN DATA DARI TABEL ANDA)
# ---------------------------------------------------------------------------

# TODO: 1. DEFINISI PROFIL IDEAL UNTUK SETIAP PERSONA
# Format: { "nama_persona": { "nama_aspek": { "nama_subkriteria": nilai_ideal, ... }, ... }, ... }
# Pastikan nama aspek dan subkriteria konsisten di semua bagian.
PROFIL_IDEAL_PERSONA = {
    "individu_lajang": {
        "KarakteristikHunian": {
            "land_area": 5,  # Contoh nilai ideal (misal skala 1-5)
            "bedrooms": 5,
            "bathrooms": 3,
            "floors": 3,
            "type": 5
        },
        "FasilitasLokasiSekitar": {
            "SCHOOL": 4, 
            "HOSPITAL": 4, 
            "TRANSPORT": 4,
            "MARKET": 4
        },
        "FasilitasHunian": {
            "facility_ac": 3,
            "facility_carport": 2,
            "facility_garasi": 2,
            "facility_garden": 2,
            "facility_stove": 3,
            "facility_oven": 2,
            "facility_refrigerator": 3,
            "facility_microwave": 2,
            "facility_pam": 3,
            "facility_water_heater": 3,
            "facility_gordyn": 2,
        }
    },
    "berkeluarga_tanpa_anak": {
        "KarakteristikHunian": {
            "land_area": 5,  # Contoh nilai ideal (misal skala 1-5)
            "bedrooms": 5,
            "bathrooms": 3,
            "floors": 3,
            "type": 5
        },
        "FasilitasLokasiSekitar": {
            "SCHOOL": 4, 
            "HOSPITAL": 4, 
            "TRANSPORT": 4,
            "MARKET": 4
        },
        "FasilitasHunian": {
            "facility_ac": 3,
            "facility_carport": 3,
            "facility_garasi": 3,
            "facility_garden": 2,
            "facility_stove": 3,
            "facility_oven": 3,
            "facility_refrigerator": 3,
            "facility_microwave": 2,
            "facility_pam": 3,
            "facility_water_heater": 3,
            "facility_gordyn": 2,
        }
    },
    "berkeluarga_dengan_anak": {
        "KarakteristikHunian": {
            "land_area": 5,  # Contoh nilai ideal (misal skala 1-5)
            "bedrooms": 5,
            "bathrooms": 3,
            "floors": 3,
            "type": 5
        },
        "FasilitasLokasiSekitar": {
            "SCHOOL": 4, 
            "HOSPITAL": 4, 
            "TRANSPORT": 4,
            "MARKET": 4
        },
        "FasilitasHunian": {
            "facility_ac": 3,
            "facility_carport": 3,
            "facility_garasi": 3,
            "facility_garden": 3,
            "facility_stove": 3,
            "facility_oven": 3,
            "facility_refrigerator": 3,
            "facility_microwave": 3,
            "facility_pam": 3,
            "facility_water_heater": 3,
            "facility_gordyn": 3,
        }
    }
}

# TODO: 2. TABEL PEMBOBOTAN NILAI GAP
# Format: { nilai_gap: bobot, ... }
# Sesuaikan dengan tabel yang Anda gunakan.
PEMBOBOTAN_GAP = {
    0: 5.0,   # Tidak ada selisih (sesuai target)
    1: 4.5,   # Kelebihan 1 tingkat dari target
   -1: 4.0,   # Kekurangan 1 tingkat dari target
    2: 3.5,   # Kelebihan 2 tingkat dari target
   -2: 3.0,   # Kekurangan 2 tingkat dari target
    3: 2.5,   # Kelebihan 3 tingkat dari target
   -3: 2.0,   # Kekurangan 3 tingkat dari target
    4: 1.5,   # Kelebihan 4 tingkat dari target
   -4: 1.0,   # Kekurangan 4 tingkat dari target
    # Tambahkan atau sesuaikan jika rentang gap atau bobotnya berbeda
    # Misalnya, jika ada gap > 4 atau < -4
}

# TODO: 3. KONFIGURASI CORE FACTOR (CF) DAN SECONDARY FACTOR (SF) PER ASPEK
# Format: { "nama_aspek": { "cf": ["subkriteria1", ...], "sf": ["subkriteria2", ...], "bobot_persen_cf": 60, "bobot_persen_sf": 40 }, ... }
# Jumlah bobot_persen_cf dan bobot_persen_sf harus 100 untuk setiap aspek.
# Pastikan nama subkriteria di sini SAMA PERSIS dengan yang ada di PROFIL_IDEAL_PERSONA.
KONFIGURASI_ASPEK = {
    "Keuangan": {
        "cf": ["Pendapatan Bersih Bulanan", "Dana Darurat (kali pengeluaran bulanan)"],
        "sf": ["Persentase Tabungan dari Pendapatan"],
        "bobot_persen_cf": 60,  # 60%
        "bobot_persen_sf": 40   # 40%
    },
    "Gaya Hidup & Kebutuhan": {
        # Contoh: untuk lajang, ukuran properti mungkin CF, tapi untuk keluarga dengan anak, jumlah kamar tidur bisa jadi CF
        # Ini perlu disesuaikan per persona jika CF/SF nya berbeda, atau dibuat generik jika sama
        # Untuk contoh ini, kita buat generik. Jika berbeda per persona, struktur data ini perlu diubah.
        "cf": ["Preferensi Ukuran Properti (Studio/1BR/2BR/dst.)", "Jumlah Kamar Tidur Ideal", "Kebutuhan Ruang Bermain Anak"], # Kebutuhan Ruang Bermain Anak & Jumlah Kamar Tidur Ideal hanya relevan untuk 'berkeluarga_dengan_anak'
        "sf": ["Kebutuhan Ruang Kerja Pribadi", "Frekuensi Aktivitas Sosial di Rumah"],
        "bobot_persen_cf": 70,
        "bobot_persen_sf": 30
    },
    "Preferensi Lokasi": {
        "cf": ["Kedekatan dengan Pusat Kota/Bisnis", "Kedekatan dengan Sekolah Berkualitas", "Keamanan Lingkungan"], # Kedekatan dengan Sekolah & Keamanan Lingkungan lebih relevan untuk 'berkeluarga_dengan_anak'
        "sf": ["Akses ke Transportasi Publik", "Kedekatan dengan Fasilitas Hiburan/Lifestyle"],
        "bobot_persen_cf": 65,
        "bobot_persen_sf": 35
    }
    # Tambahkan konfigurasi untuk aspek lain jika ada
}

# TODO: 4. BOBOT ANTAR ASPEK (OPSIONAL)
# Jika setiap aspek memiliki bobot yang berbeda dalam menentukan skor akhir persona.
# Format: { "nama_aspek": bobot_persentase, ... }
# Jumlah semua bobot persentase harus 100.
# Jika tidak digunakan (semua aspek dianggap sama penting), set ke None atau {}
BOBOT_ANTAR_ASPEK = {
    "KarakteristikHunian": 40,                 # 40%
    "FasilitasLokasiSekitar": 30,   # 35%
    "FasilitasHunian": 30         # 25%
}
# Jika BOBOT_ANTAR_ASPEK adalah None atau {}, maka skor akhir persona akan dihitung sebagai rata-rata dari nilai total setiap aspek.


# TODO: 5. CONTOH INPUT USER DARI TABEL UJI COBA
# Format: { "nama_aspek": { "nama_subkriteria": nilai_user, ... }, ... }
# Pastikan nama aspek dan subkriteria konsisten.
INPUT_USER_UJI = {
    "Keuangan": {
        "Pendapatan Bersih Bulanan": 4,
        "Persentase Tabungan dari Pendapatan": 3,
        "Dana Darurat (kali pengeluaran bulanan)": 2 # User ini kurang dana daruratnya
    },
    "Gaya Hidup & Kebutuhan": {
        "Preferensi Ukuran Properti (Studio/1BR/2BR/dst.)": 3, # User ingin 2BR
        "Kebutuhan Ruang Kerja Pribadi": 5, # User sangat butuh ruang kerja
        "Frekuensi Aktivitas Sosial di Rumah": 2,
        "Kebutuhan Ruang Bermain Anak": 1, # User tidak butuh ruang main anak (skala 1-5, 1=tidak butuh)
        "Jumlah Kamar Tidur Ideal": 3 # User ingin 2KT
    },
    "Preferensi Lokasi": {
        "Kedekatan dengan Pusat Kota/Bisnis": 4,
        "Akses ke Transportasi Publik": 5,
        "Kedekatan dengan Fasilitas Hiburan/Lifestyle": 3,
        "Kedekatan dengan Sekolah Berkualitas": 1, # User tidak prioritas sekolah (skala 1-5, 1=tidak prioritas)
        "Keamanan Lingkungan": 3
    }
}

# ---------------------------------------------------------------------------
# BAGIAN 2: FUNGSI-FUNGSI PERHITUNGAN PROFILE MATCHING
# ---------------------------------------------------------------------------

def hitung_gap(nilai_user, nilai_ideal):
    """Menghitung selisih (gap) antara nilai user dan nilai ideal."""
    return nilai_user - nilai_ideal

def dapatkan_bobot_gap(nilai_gap, tabel_pemetaan_gap):
    """Mengonversi nilai gap menjadi bobot berdasarkan tabel pemetaan."""
    # Cari nilai gap terdekat jika tidak ada yang persis sama (opsional, untuk sekarang pakai .get())
    return tabel_pemetaan_gap.get(nilai_gap, 0) # Default bobot 0 jika gap tidak ada di tabel

def hitung_profile_matching(data_profil_ideal, data_input_user, pemetaan_bobot_gap, konfigurasi_aspek, bobot_antar_aspek=None):
    """
    Melakukan seluruh proses perhitungan Profile Matching.
    """
    hasil_skor_persona = {}

    print("Memulai Perhitungan Profile Matching...\n")

    for nama_persona, aspek_ideal_persona in data_profil_ideal.items():
        print(f"--- Menghitung untuk Persona: {nama_persona} ---")
        nilai_akhir_persona = 0
        total_bobot_aspek_digunakan = 0 # Untuk pembobotan antar aspek
        nilai_total_semua_aspek = 0 # Untuk rata-rata jika tidak ada bobot antar aspek
        jumlah_aspek_valid_untuk_rata_rata = 0

        for nama_aspek, subkriteria_ideal in aspek_ideal_persona.items():
            # Periksa apakah aspek ada di input user dan konfigurasi
            if nama_aspek not in data_input_user:
                print(f"  Peringatan: Aspek '{nama_aspek}' tidak ada dalam input user. Aspek ini dilewati untuk persona {nama_persona}.")
                continue
            if nama_aspek not in konfigurasi_aspek:
                print(f"  Peringatan: Konfigurasi CF/SF untuk aspek '{nama_aspek}' tidak ditemukan. Aspek ini dilewati.")
                continue

            subkriteria_user = data_input_user[nama_aspek]
            config_aspek_saat_ini = konfigurasi_aspek[nama_aspek]

            print(f"  Aspek: {nama_aspek}")

            # Hitung bobot untuk setiap sub-kriteria
            bobot_subkriteria_cf = []
            bobot_subkriteria_sf = []

            for nama_sub_ideal, nilai_ideal in subkriteria_ideal.items():
                # Hanya proses subkriteria yang ada di CF atau SF konfigurasi aspek saat ini
                # DAN subkriteria tersebut ada di input user untuk aspek tersebut
                is_cf = nama_sub_ideal in config_aspek_saat_ini.get("cf", [])
                is_sf = nama_sub_ideal in config_aspek_saat_ini.get("sf", [])

                if not (is_cf or is_sf): # Jika subkriteria ideal tidak terdaftar di CF/SF aspek ini, skip
                    # Ini bisa terjadi jika PROFIL_IDEAL_PERSONA punya subkriteria yang tidak masuk CF/SF di KONFIGURASI_ASPEK
                    # Atau jika satu persona punya subkriteria yang tidak dimiliki persona lain (misal 'Kebutuhan Ruang Bermain Anak')
                    # print(f"    Info: Sub-kriteria ideal '{nama_sub_ideal}' tidak terdaftar di CF/SF untuk aspek '{nama_aspek}'.")
                    continue


                if nama_sub_ideal not in subkriteria_user:
                    print(f"    Peringatan: Sub-kriteria '{nama_sub_ideal}' di aspek '{nama_aspek}' tidak ada dalam input user. Menggunakan bobot 0.")
                    # Jika subkriteria penting (misal CF) tidak diisi user, ini bisa jadi masalah.
                    # Alternatif: assign nilai default atau bobot terendah. Untuk sekarang, bobot 0.
                    gap_val = None # Atau hitung gap dengan nilai user default (misal 0 atau 1)
                    bobot = 0
                else:
                    nilai_user = subkriteria_user[nama_sub_ideal]
                    gap_val = hitung_gap(nilai_user, nilai_ideal)
                    bobot = dapatkan_bobot_gap(gap_val, pemetaan_bobot_gap)
                
                print(f"    Sub: {nama_sub_ideal} (Ideal: {nilai_ideal}, User: {subkriteria_user.get(nama_sub_ideal, 'N/A')}, Gap: {gap_val if gap_val is not None else 'N/A'}, Bobot: {bobot})")

                if is_cf:
                    bobot_subkriteria_cf.append(bobot)
                elif is_sf:
                    bobot_subkriteria_sf.append(bobot)

            # Hitung nilai rata-rata CF dan SF
            nilai_rata_cf = sum(bobot_subkriteria_cf) / len(bobot_subkriteria_cf) if bobot_subkriteria_cf else 0
            nilai_rata_sf = sum(bobot_subkriteria_sf) / len(bobot_subkriteria_sf) if bobot_subkriteria_sf else 0
            print(f"    Nilai Rata-rata CF: {nilai_rata_cf:.2f} (dari {len(bobot_subkriteria_cf)} sub-kriteria CF)")
            print(f"    Nilai Rata-rata SF: {nilai_rata_sf:.2f} (dari {len(bobot_subkriteria_sf)} sub-kriteria SF)")

            # Hitung nilai total aspek
            persen_cf = config_aspek_saat_ini["bobot_persen_cf"] / 100.0
            persen_sf = config_aspek_saat_ini["bobot_persen_sf"] / 100.0
            nilai_total_aspek = (nilai_rata_cf * persen_cf) + (nilai_rata_sf * persen_sf)
            print(f"    Nilai Total Aspek '{nama_aspek}': {nilai_total_aspek:.2f}")

            # Akumulasi untuk skor akhir persona
            if bobot_antar_aspek and nama_aspek in bobot_antar_aspek:
                bobot_aspek_ini = bobot_antar_aspek[nama_aspek] / 100.0
                nilai_akhir_persona += nilai_total_aspek * bobot_aspek_ini
                total_bobot_aspek_digunakan += bobot_aspek_ini
            else: # Jika tidak ada bobot antar aspek atau aspek ini tidak terdaftar, gunakan rata-rata
                nilai_total_semua_aspek += nilai_total_aspek
                jumlah_aspek_valid_untuk_rata_rata += 1
        
        # Finalisasi skor persona
        if bobot_antar_aspek and total_bobot_aspek_digunakan > 0:
            # Jika total bobot aspek yang digunakan kurang dari 1 (misal ada aspek di BOBOT_ANTAR_ASPEK tapi tidak ada di input user/persona),
            # kita bisa normalisasi atau biarkan apa adanya. Untuk sekarang, biarkan.
            pass # nilai_akhir_persona sudah terakumulasi dengan bobotnya
        elif jumlah_aspek_valid_untuk_rata_rata > 0:
            nilai_akhir_persona = nilai_total_semua_aspek / jumlah_aspek_valid_untuk_rata_rata
        else:
            nilai_akhir_persona = 0 # Jika tidak ada aspek yang bisa dihitung

        hasil_skor_persona[nama_persona] = nilai_akhir_persona
        print(f"  SKOR AKHIR Persona '{nama_persona}': {nilai_akhir_persona:.3f}\n")

    return hasil_skor_persona

def rangking_persona(hasil_skor):
    """Merangking persona berdasarkan skor tertinggi."""
    if not hasil_skor:
        return []
    # Mengurutkan persona dari skor tertinggi ke terendah
    peringkat = sorted(hasil_skor.items(), key=lambda item: item[1], reverse=True)
    return peringkat

# ---------------------------------------------------------------------------
# BAGIAN 3: EKSEKUSI UTAMA
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Validasi awal sederhana (bisa diperluas)
    if not PROFIL_IDEAL_PERSONA or not INPUT_USER_UJI or not PEMBOBOTAN_GAP or not KONFIGURASI_ASPEK:
        print("Kesalahan: Data konfigurasi (PROFIL_IDEAL_PERSONA, INPUT_USER_UJI, PEMBOBOTAN_GAP, atau KONFIGURASI_ASPEK) ada yang kosong.")
    else:
        skor_persona = hitung_profile_matching(
            PROFIL_IDEAL_PERSONA,
            INPUT_USER_UJI,
            PEMBOBOTAN_GAP,
            KONFIGURASI_ASPEK,
            BOBOT_ANTAR_ASPEK
        )

        print("\n--- Hasil Perhitungan Skor Akhir untuk Setiap Persona ---")
        for persona, skor in skor_persona.items():
            print(f"Persona: {persona:<30} Skor: {skor:.3f}")

        peringkat_hasil = rangking_persona(skor_persona)

        print("\n--- Hasil Perangkingan Persona ---")
        if peringkat_hasil:
            for i, (persona, skor) in enumerate(peringkat_hasil):
                print(f"{i+1}. Persona: {persona:<30} Skor: {skor:.3f}")

            persona_terpilih = peringkat_hasil[0][0]
            skor_terpilih = peringkat_hasil[0][1]
            print(f"\n==> Persona yang paling sesuai untuk user adalah: ✨ {persona_terpilih} ✨ (Skor: {skor_terpilih:.3f})")
        else:
            print("Tidak dapat menentukan persona. Periksa kembali data dan perhitungan.")

