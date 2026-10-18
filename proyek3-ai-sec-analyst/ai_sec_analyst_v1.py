import os
import json
from google import genai

def load_incident_report(json_path):
    """Membaca file JSON laporan insiden hasil deteksi Proyek 2."""
    if not os.path.exists(json_path):
        print(f"[-] ERROR: File '{json_path}' tidak ditemukan.")
        print("    Pastikan Proyek 2 sudah menghasilkan incident_report.json!")
        return None
    
    with open(json_path, "r") as file:
        return json.load(file)

def generate_ai_analysis(incidents_data):
    """Mengirim data insiden ke Gemini API menggunakan System Prompt keamanan."""
    
    # 1. Ambil API Key dari Environment Variable
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[-] ERROR: GEMINI_API_KEY belum diset di terminal environment variable.")
        print("    Jalankan: export GEMINI_API_KEY='your_api_key_here'")
        return None
    
    # 2. Inisialisasi Client Gemini
    client = genai.Client(api_key=api_key)
    
    # 3. Buat System Instruction (Instruksi Peran untuk AI)
    system_instruction = (
        "Anda adalah seorang Senior SOC Security Analyst dan Incident Response Specialist. "
        "Tugas Anda adalah menganalisis data insiden serangan siber dari log server dan memberikan "
        "laporan analisis risiko serta rekomendasi perbaikan (Actionable Remediation Plan) yang konkret."
    )
    
    # 4. Ubah data JSON ke bentuk teks biasa (string)
    incidents_json_text = json.dumps(incidents_data, indent=2)
    
    # 5. Susun teks instruksi (prompt) yang akan dikirimkan ke AI
    user_prompt = (
        "Berikut adalah daftar insiden keamanan terstruktur yang terdeteksi dari log server (dalam format JSON):\n\n"
        + incidents_json_text + "\n\n"
        "Tolong buatkan Laporan Analisis Keamanan Eksekutif dengan struktur berikut:\n"
        "1. **Ringkasan Insiden (Executive Summary)**: Rangkuman singkat ancaman yang terjadi.\n"
        "2. **Analisis Akar Masalah (Root Cause Analysis)**: Detail teknis tiap jenis serangan (Brute Force, SQLi, Path Traversal) dan dampaknya.\n"
        "3. **Rencana Mitigasi Taktis (Actionable Remediation Plan)**:\n"
        "   - Langkah cepat (penanganan IP penyerang/firewall).\n"
        "   - Perbaikan kode/aplikasi (misal: sanitasi input SQL, rate limiting).\n"
        "4. **Tingkat Urgensi Response**: Berikan prioritas tindakan (High/Critical)."
    )
    
    print("[*] Mengirimkan data insiden ke AI Security Analyst (Gemini API)...")
    
    try:
        # 6. Panggil Gemini API menggunakan model gemini-3.8-flash
        response = client.models.generate_content(
            model='gemini-3.8-flash',
            contents=user_prompt,
            config={'system_instruction': system_instruction}
        )
        return response.text
    except Exception as e:
        print(f"[-] Gagal menghubungi Gemini API: {e}")
        return None

def save_report_to_md(report_text, output_path="ai_remediation_report.md"):
    """Menyimpan hasil analisis AI ke file Markdown."""
    with open(output_path, "w") as file:
        file.write(report_text)
    print(f"[+] Laporan analisis AI berhasil disimpan ke: '{output_path}'")

def main():
    print("=" * 70)
    print(" 🤖 PROYEK 3: AI SECURITY ANALYST & INCIDENT RESPONSE")
    print("=" * 70)
    
    # Lokasi file JSON dari Proyek 2
    json_path = "../proyek2-sec-monitoring/incident_report.json"
    
    # 1. Baca data insiden
    incidents = load_incident_report(json_path)
    if not incidents:
        return
    
    print(f"[+] Berhasil memuat {len(incidents)} insiden dari '{json_path}'")
    
    # 2. Kirim data ke AI untuk dianalisis
    ai_report = generate_ai_analysis(incidents)
    
    if ai_report:
        print("\n" + "=" * 70)
        print("📄 HASIL ANALISIS AI SECURITY ANALYST:")
        print("=" * 70 + "\n")
        print(ai_report)
        print("\n" + "=" * 70)
        
        # 3. Simpan hasil analisis ke file Markdown
        save_report_to_md(ai_report)

if __name__ == "__main__":
    main()