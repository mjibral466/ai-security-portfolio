import os
from google import genai

# Membaca API Key dari environment variable terminal
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    print("[-] GEMINI_API_KEY belum di-export di terminal!")
    print("    Silakan jalankan: export GEMINI_API_KEY='API_KEY_ANDA'")
else:
    try:
        # Inisialisasi client Gemini
        client = genai.Client(api_key=api_key)
        
        # Mengirimkan permintaan tes ke model Gemini
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents="Tes koneksi API key",
        )
        
        print("[+] API Key BERHASIL & AKTIF! Balasan dari AI:")
        print(f"    '{response.text.strip()}'")
        
    except Exception as e:
        print("[-] API Key GAGAL / ERROR:")
        print(e)