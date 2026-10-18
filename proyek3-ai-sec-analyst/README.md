# 🤖 Proyek 3: AI Security Analyst & Incident Response

Sistem analisis keamanan berbasis Kecerdasan Buatan (AI) yang mengintegrasikan **Large Language Model (LLM)** via API untuk membaca laporan insiden terstruktur (JSON), menganalisis akar masalah (*Root Cause Analysis*), serta menyusun *Actionable Remediation Plan* secara otomatis.

---

## 🚀 Fitur Utama

1. **Context Injection & Grounding**:
   - Menyisipkan data insiden nyata dari Proyek 2 (`incident_report.json`) secara terstruktur ke dalam instruksi AI tanpa berhalusinasi.
2. **System Prompting Berstandar SOC**:
   - Mengatur peran AI sebagai *Senior SOC Analyst & Incident Response Specialist* untuk menghasilkan analisis risiko dan tingkat urgensi tindakan (*High/Critical*).
3. **Automated Report Generation**:
   - Menghasilkan laporan mitigasi teknis dan eksekutif secara instan dalam format Markdown (`ai_remediation_report.md`).
4. **Google Gemini API Integration**:
   - Menggunakan model LLM terbaru (`gemini-3.8-flash`) dengan manajemen *API Key* yang aman via *Environment Variable*.

---

## 🛠️ Arsitektur Alur Kerja

```text

[ access.log ] ➔ [ Proyek 2 Log Parser ] ➔ [ incident_report.json ] ➔ [ Proyek 3 AI Analyst ] ➔ [ ai_remediation_report.md ]

🛠️ Struktur Berkas

ai_sec_analyst_v1.py : Skrip utama integrasi Gemini API & pembaca data JSON insiden.
ai_remediation_report.md : Laporan mitigasi keamanan otomatis hasil generate AI.
test.py : Skrip pengujian koneksi dan validasi API Key.
🧪 Cara Menjalankan

Set API Key di terminal:
export GEMINI_API_KEY="your_api_key_here"

Jalankan skrip AI Analyst:
python3 ai_sec_analyst_v1.py

Baca hasil laporan mitigasi AI:
cat ai_remediation_report.md



Simpan berkas tersebut (**`Ctrl + S`**).

