# AI-WaiZ

# AI WhatsApp Document Assistant

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
## Deskripsi Proyek

**AI WhatsApp Document Assistant** adalah sebuah chatbot berbasis WhatsApp yang dirancang untuk membantu pengguna dalam membuat, mengedit, dan mengelola dokumen (DOCX dan PDF) secara interaktif melalui percakapan teks atau suara di platform WhatsApp. Proyek ini berfokus pada kemudahan penyusunan dan modifikasi teks, terutama untuk keperluan seperti pembuatan makalah, laporan, atau karya tulis lainnya.

Tujuan utama proyek ini adalah menyediakan antarmuka yang intuitif menggunakan bahasa natural untuk berinteraksi dengan dokumen tanpa memerlukan aplikasi pengolah kata tradisional di perangkat pengguna.

## Fitur Utama

Berdasarkan kerangka yang diusulkan, fitur-fitur utama proyek ini meliputi:

### I. Pembuatan Dokumen Baru
* **Inisiasi:** Membuat dokumen baru dengan perintah natural, menentukan judul dan format (DOCX/PDF).
* **Input Konten:** Menambahkan konten awal dokumen melalui teks langsung atau transkripsi pesan suara.
* **Struktur Otomatis:** AI dapat menyarankan dan membuat struktur dasar dokumen (misalnya, Pendahuluan, Isi, Kesimpulan untuk makalah).
* **(Opsional) Template Dasar:** Pengguna dapat memilih dari beberapa template dokumen sederhana.

### II. Pengeditan Dokumen
* **Seleksi Dokumen:** Memilih dokumen aktif untuk diedit (dokumen terakhir atau menyebutkan judul).
* **Edit Teks:** Menambah, menghapus, mengganti, atau memindahkan blok teks (paragraf, kalimat) menggunakan perintah.
* **Pemformatan Teks Dasar:** Menerapkan format tebal, miring, garis bawah, serta membuat judul/subjudul.
* **Daftar (List):** Membuat daftar bernomor atau berpoin dari teks.
* **Struktur Dokumen:** Menambah bagian baru atau mengubah urutan bagian yang sudah ada.
* **Daftar Isi (Sederhana):** Membuat daftar isi otomatis berdasarkan judul/subjudul.

### III. Manajemen Konten & Referensi (Khusus Karya Tulis)
* **Kutipan:** Membantu memformat kutipan dasar.
* **Daftar Pustaka:** Membantu menyusun daftar pustaka dasar dalam format standar (misalnya, APA, MLA).
* **(Opsional) Pencarian Informasi:** Melakukan pencarian web sederhana untuk bahan referensi cepat.

### IV. Konversi dan Ekspor Dokumen
* **Konversi Format:** Mengonversi dokumen DOCX menjadi PDF.
* **Ekspor/Unduh:** Mengirim file dokumen yang sudah selesai (DOCX atau PDF) langsung ke chat pengguna.

### V. Fitur Tambahan
* **Riwayat Revisi Sederhana:** Melihat versi terakhir atau membatalkan tindakan.
* **Pemeriksaan Ejaan dan Tata Bahasa Dasar:** Memberikan saran perbaikan.
* **Ringkasan Dokumen:** Membuat ringkasan singkat dari isi dokumen.
* **Penghitungan Kata/Karakter:** Memberikan informasi statistik dokumen.
* **Bantuan Pengguna:** Menyediakan daftar perintah dan panduan penggunaan.
* **(Opsional) Personalisasi:** Mengingat preferensi pengguna.

## Struktur Proyek

Proyek ini diorganisir ke dalam beberapa file dan modul utama:

```
/nama_folder_proyek/
├── .env             # Variabel lingkungan (kredensial sensitif)
├── config.py        # Konfigurasi aplikasi dan API (membaca dari .env)
├── run.py           # Script utama untuk menjalankan aplikasi Flask
├── app.py           # Aplikasi Flask, menangani webhook dan alur pesan utama
├── document_processor.py # Modul untuk logika pembuatan, pengeditan, dan konversi dokumen
├── nlp_engine.py    # Modul untuk Natural Language Processing (deteksi intent & entity)
├── storage_manager.py # Modul untuk mengelola penyimpanan file dokumen dan data sesi
├── media_handler.py # (TODO) Modul untuk mengunduh/mengunggah media dari/ke WhatsApp API
└── audio_transcriber.py # (TODO) Modul untuk transkripsi pesan suara
├── temp_storage/    # Direktori penyimpanan sementara (sesuai config)
│   ├── documents/
│   └── sessions/
└── (dll...)         # File dan folder lain yang mungkin dibutuhkan
```

## Tata Cara Menggunakan Program (Untuk Developer)

Berikut adalah langkah-langkah untuk melakukan setup dan menjalankan aplikasi ini di lingkungan development Anda:

### 1. Persiapan Lingkungan

1.  **Clone Repositori:** Jika kode berada di repositori, clone ke mesin lokal Anda. Jika tidak, pastikan semua file (`.env`, `config.py`, `app.py`, `run.py`, modul-modul Python, dll.) berada dalam satu direktori proyek.
2.  **Buat Virtual Environment:** Buka terminal atau command prompt di direktori proyek.
    ```bash
    python -m venv docassistant-env
    ```
3.  **Aktifkan Virtual Environment:**
    * Di Windows:
        ```bash
        docassistant-env\Scripts\activate
        ```
    * Di macOS/Linux:
        ```bash
        source docassistant-env/bin/activate
        ```
4.  **Instal Dependensi Python:** Pastikan virtual environment aktif, lalu instal paket yang diperlukan.
    ```bash
    pip install -r requirements.txt
    ```
    *(Catatan: Anda perlu membuat file `requirements.txt` yang berisi daftar paket. Alternatifnya, Anda bisa langsung menginstal seperti ini, tapi membuat `requirements.txt` adalah praktik yang baik):*
    ```bash
    pip install flask requests python-dotenv python-docx docx2pdf uuid redis # Tambahkan library NLP/transkripsi nanti
    ```

### 2. Setup WhatsApp Business API

1.  **Dapatkan Akses API:** Daftar atau gunakan akun Meta for Developers, buat aplikasi, dan atur produk WhatsApp API. Ikuti panduan Meta untuk mendapatkan nomor telepon bisnis dan akses API.
2.  **Dapatkan Kredensial:** Dari dashboard aplikasi Meta Anda, catat:
    * ID Akun Bisnis WhatsApp (`WHATSAPP_BUSINESS_ACCOUNT_ID`)
    * ID Nomor Telepon Pengirim (`WHATSAPP_PHONE_NUMBER_ID`)
    * Token Akses Permanen (`WHATSAPP_API_TOKEN`)
    * Token Verifikasi Webhook yang Anda tentukan sendiri (`WEBHOOK_VERIFY_TOKEN`).
3.  **Isi File `.env`:** Buka file `.env` di direktori proyek Anda dan isi dengan kredensial yang Anda dapatkan.
    ```dotenv
    # .env - Variabel Lingkungan untuk WhatsApp Document Assistant

    WEBHOOK_VERIFY_TOKEN="ganti_dengan_token_verifikasi_aman_Anda"
    WHATSAPP_API_TOKEN="ganti_dengan_TOKEN_AKSES_API_WHATSAPP_Anda"
    WHATSAPP_PHONE_NUMBER_ID="ganti_dengan_ID_NOMOR_TELEPON_WHATSAPP_Anda"
    WHATSAPP_BUSINESS_ACCOUNT_ID="ganti_dengan_ID_AKUN_BISNIS_WHATSAPP_Anda"
    TEMP_STORAGE_PATH="./temp_storage"
    DOCUMENT_TTL=3600 # Waktu dokumen disimpan sementara dalam detik
    HOST="0.0.0.0"
    PORT=5000
    FLASK_DEBUG="True" # Set True untuk mode debug
    ```
    *(Pastikan nilai token verifikasi webhook di `.env` sama dengan yang Anda masukkan di dashboard Meta saat mengkonfigurasi webhook).*

### 3. Konfigurasi Webhook di Meta for Developers

Aplikasi Anda perlu bisa diakses dari internet agar WhatsApp bisa mengirim pesan ke endpoint `/webhook` Anda.

1.  **Siapkan URL Publik:**
    * Untuk development lokal, Anda bisa menggunakan alat seperti **ngrok** untuk mengekspos server lokal Anda ke internet. Jalankan ngrok dan catat URL HTTPS publik yang diberikan (misalnya, `https://abcdef123456.ngrok-free.app`).
    * Untuk deployment produksi, Anda akan menggunakan nama domain publik server Anda.
2.  **Atur Webhook di Dashboard Meta:**
    * Masuk ke dashboard aplikasi Meta for Developers Anda.
    * Navigasi ke bagian **WhatsApp -> Configuration**.
    * Di bagian **Webhook**, klik **Edit**.
    * Masukkan **Callback URL** lengkap Anda (`URL_PUBLIK_NGROK_ATAU_SERVER/webhook`, contoh: `https://abcdef123456.ngrok-free.app/webhook`).
    * Masukkan **Verify Token** yang sama persis dengan nilai `WEBHOOK_VERIFY_TOKEN` di file `.env` Anda.
    * Klik **Verify and Save**. Meta akan mengirim permintaan GET ke URL Anda untuk verifikasi. Jika berhasil, status akan hijau.
    * Setelah berhasil verifikasi, di bagian **Webhook fields**, klik **Manage** dan **Subscribe** pada field `messages`. Ini agar Anda menerima notifikasi pesan masuk.

### 4. Menjalankan Aplikasi

Setelah lingkungan dan konfigurasi siap, Anda bisa menjalankan aplikasi Flask menggunakan script `run.py`:

1.  Pastikan virtual environment Anda aktif.
2.  Pastikan Anda berada di direktori utama proyek yang berisi `run.py`.
3.  Jalankan script:
    ```bash
    python run.py
    ```
    Anda bisa menambahkan argumen opsional:
    ```bash
    python run.py --port 8000 --debug
    ```
    * `--port`: Menentukan port yang akan digunakan (default 5000, atau dari variabel lingkungan `PORT`).
    * `--debug`: Mengaktifkan mode debug Flask (default False, atau dari variabel lingkungan `FLASK_DEBUG`).

Aplikasi akan berjalan dan mendengarkan permintaan POST dari webhook WhatsApp di endpoint `/webhook`. Log aktivitas akan ditampilkan di konsol.

### 5. Interaksi dengan Asisten (Untuk End User)

Setelah aplikasi berjalan dan webhook terkonfigurasi, pengguna dapat berinteraksi dengan asisten melalui nomor WhatsApp bisnis Anda:

* Kirim pesan teks atau pesan suara.
* Gunakan perintah bahasa natural sesuai fitur yang diimplementasikan (misalnya, "Buat dokumen baru tentang revolusi industri", "Tambahkan paragraf ini ke bagian pendahuluan", "Ekspor dokumen sebagai PDF", "Bantuan").
* Kirim file dokumen DOCX atau PDF untuk mulai mengeditnya.

## Status Pengembangan & Langkah Selanjutnya (Untuk Developer)

Perlu diingat bahwa kode yang ada saat ini merupakan kerangka dasar dengan implementasi *placeholder* untuk banyak fungsionalitas kompleks (seperti transkripsi audio, pengunduhan/pengunggahan media yang lengkap, manipulasi dokumen yang canggih, dan NLP yang robust).

Langkah-langkah pengembangan selanjutnya (sesuai dengan 12 langkah yang dibahas sebelumnya) melibatkan pengisian implementasi nyata di modul-modul seperti `document_processor.py`, `nlp_engine.py` (mungkin mengganti regex dengan framework NLP sungguhan), `storage_manager.py`, `media_handler.py`, dan `audio_transcriber.py`.

## Kontribusi

## Lisensi

Proyek ini dilisensikan di bawah Lisensi MIT. Lihat file `LICENSE` untuk detail selengkapnya.

