# 🛡️ Proyek 2: Security Monitoring & Log Analysis Engine

Sistem pemantau keamanan otomatis berbasis Python yang dirancang untuk mengurai (*parsing*) berkas *access log* server web (Apache/Nginx), mendeteksi indikasi serangan siber secara *real-time*, dan menghasilkan laporan insiden terstruktur dalam format **JSON**.

Dokumentasi ini berfungsi sebagai panduan dan penjelas bagi siapa saja yang mengunjungi repositori GitHub Anda.

---

## 📝 Langkah Pembuatan Berkas `README.md` di VS Code / WSL

1. Buka terminal WSL Anda dan pastikan berada di folder direktori proyek:
   ```bash
   cd ~/proyek2-sec-monitoring
Buka editor VS Code untuk membuat/mengedit berkas README.md:

Bash
code README.md
Salin dan tempelkan seluruh teks dokumentasi di bawah ini ke dalam editor, lalu simpan berkas (Ctrl + S).

🚀 Fitur Utama
Log Parsing Engine (re / Regex):

Mengurai teks mentah access log menjadi data terstruktur (IP Address, Timestamp, HTTP Method, URL Endpoint, Status Code, dan Response Size).

Detection Rules Engine:

Brute Force Detector: Mendeteksi percobaan login gagal berulang (HTTP Status 401) yang melebihi ambang batas (threshold).

SQL Injection (SQLi) Detector: Memindai muatan (payload) manipulasi basis data pada parameter URL.

Directory / Path Traversal Detector: Mendeteksi percobaan navigasi folder (../) dan akses berkas sensitif sistem (/etc/passwd).

Machine-Readable Export:

Mengekspor hasil laporan insiden secara otomatis ke format JSON (incident_report.json) agar siap diintegrasikan dengan sistem SIEM atau pipeline analisis AI.

🛠️ Struktur Berkas
Plaintext
.
├── access.log            # Sampel berkas log lalu lintas web
├── log_parser_v1.py      # Skrip pengurai log dasar
├── log_parser_v2.py      # Skrip utama pemindai ancaman & pembuat laporan JSON
└── incident_report.json  # Berkas luaran laporan insiden keamanan
🧪 Cara Menjalankan
Pastikan berkas access.log dan log_parser_v2.py berada di dalam direktori yang sama.

Jalankan skrip utama menggunakan Python 3:

Bash
python3 log_parser_v2.py
Untuk melihat hasil laporan insiden format JSON yang telah dihasilkan:

Bash
# Menampilkan isi file JSON mentah:
cat incident_report.json

# Menampilkan isi file JSON dengan format terstruktur & berwarna (jika jq terpasang):
jq . incident_report.json