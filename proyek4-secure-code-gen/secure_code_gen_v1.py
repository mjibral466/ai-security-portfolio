import os
import subprocess
import json
from google import genai


def strip_markdown(text):
    """Membersihkan tag markdown code block jika AI tetap menambahkannya."""
    code = text.strip()
    if code.startswith("```python"):
        code = code[9:]
    elif code.startswith("```"):
        code = code[3:]
    if code.endswith("```"):
        code = code[:-3]
    return code.strip()


def generate_initial_code(prompt, client):
    """Meminta AI menghasilkan kode Python berdasarkan instruksi pengguna."""
    system_instruction = (
        "Anda adalah seorang Python Developer. "
        "Tuliskan HANYA kode Python murni tanpa penjelasan atau markdown tambahan. "
        "Jangan sertakan backtick ```python atau ```."
    )

    print("[*] Mengirimkan permintaan kode ke Gemini API...")
    try:
        # Menggunakan model gemini-3.8-flash
        response = client.models.generate_content(
            model='gemini-3.8-flash',
            contents=prompt,
            config={'system_instruction': system_instruction}
        )
        return strip_markdown(response.text)
    except Exception as e:
        print(f"[-] Gagal generate kode awal: {e}")
        return None


def run_sast_scan(file_path):
    """Memindai file kode menggunakan tool SAST Bandit dan mengembalikan hasil analisis."""
    print(f"[*] Memindai keamanan kode di '{file_path}' dengan Bandit (SAST)...")

    # Jalankan perintah bandit dengan output format JSON
    cmd = ["bandit", "-f", "json", "-q", file_path]
    result = subprocess.run(cmd, capture_output=True, text=True)

    try:
        sast_output = json.loads(result.stdout)
        return sast_output.get("results", [])
    except Exception as e:
        print(f"[-] Gagal membaca output Bandit: {e}")
        return []


def refactor_code(code, vulnerabilities, client):
    """Meminta AI memperbaiki kode berdasarkan temuan SAST Bandit."""
    system_instruction = (
        "Anda adalah seorang Senior DevSecOps Engineer. "
        "Tugas Anda adalah memperbaiki kerentanan keamanan pada kode Python yang terdeteksi oleh SAST tool Bandit. "
        "Kembalikan HANYA kode Python yang sudah diperbaiki tanpa penjelasan atau markdown tambahan."
    )

    vuln_summary = "\n".join([
        f"- Issue: {v.get('issue_text')} (Severity: {v.get('issue_severity')}, Line: {v.get('line_number')})"
        for v in vulnerabilities
    ])

    fence = "`" * 3
    prompt = (
        "Kode berikut memiliki celah keamanan yang terdeteksi oleh SAST Bandit:\n\n"
        f"{fence}python\n{code}\n{fence}\n\n"
        f"Daftar Kerentanan:\n{vuln_summary}\n\n"
        "Tolong perbaiki kode di atas agar 100% bebas dari celah keamanan tersebut!"
    )

    print("[!] Mengirimkan temuan SAST ke AI untuk Auto-Refactoring...")
    try:
        response = client.models.generate_content(
            model='gemini-3.8-flash',
            contents=prompt,
            config={'system_instruction': system_instruction}
        )
        return strip_markdown(response.text)
    except Exception as e:
        print(f"[-] Gagal melakukan refactoring: {e}")
        return None


def main():
    print("=" * 70)
    print(" 🛡️ PROYEK 4: AI SECURE CODE GENERATOR & AUTOMATED SAST SCANNER")
    print("=" * 70)

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[-] ERROR: GEMINI_API_KEY belum diset di terminal environment variable.")
        print("    Jalankan: export GEMINI_API_KEY='your_api_key_here'")
        return

    client = genai.Client(api_key=api_key)

    user_prompt = "Buatkan fungsi Python untuk memverifikasi password user dan menjalankan query SQL login ke database SQLite."
    print(f"[+] User Prompt: \"{user_prompt}\"\n")

    current_code = generate_initial_code(user_prompt, client)

    # Validasi: Hentikan jika kode gagal digenerate oleh AI
    if not current_code:
        print("[-] Proses dihentikan karena pembuatan kode awal gagal.")
        return

    temp_filename = "temp_generated_code.py"
    max_attempts = 3

    for attempt in range(1, max_attempts + 1):
        print(f"\n--- Iterasi SAST {attempt}/{max_attempts} ---")

        # 1. Simpan kode ke file sementara
        with open(temp_filename, "w", encoding="utf-8") as f:
            f.write(current_code)

        # 2. Pindai dengan SAST Bandit
        vulns = run_sast_scan(temp_filename)

        if not vulns:
            print("[+] KODE 100% AMAN! Tidak ditemukan kerentanan oleh SAST Bandit. 🎉")
            break
        else:
            print(f"[!] Terdeteksi {len(vulns)} celah keamanan!")
            for v in vulns:
                print(f"    - [{v.get('issue_severity')}] {v.get('issue_text')} (Baris {v.get('line_number')})")

            if attempt < max_attempts:
                refactored = refactor_code(current_code, vulns, client)
                if refactored:
                    current_code = refactored
                else:
                    print("[-] Refactoring gagal, menghentikan iterasi.")
                    break
            else:
                print("[!] Batas maksimum refactoring tercapai.")

    # 3. Simpan hasil kode aman akhir
    output_filename = "secure_output.py"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(current_code)

    print(f"\n[+] Kode hasil akhir berhasil disimpan di: '{output_filename}'")


if __name__ == "__main__":
    main()