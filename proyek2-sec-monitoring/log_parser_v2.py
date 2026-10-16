from collections import defaultdict
import json
import re

# Pola Regex standar untuk parsing access log (Nginx / Apache)
LOG_PATTERN = (
    r'(\d+\.\d+\.\d+\.\d+)\s+-\s+-\s+\[(.*?)\]\s+"(\w+)\s+(.*?)\s+HTTP/.*?"\s+(\d+)\s+(\d+)'
)

# Pola kata kunci serangan web
SQLI_PATTERNS = [r"(\%27)|(\')", r"(%20OR%20)|(\s+OR\s+)", r"UNION\s+SELECT"]
PATH_TRAVERSAL_PATTERNS = [r"\.\./", r"/etc/passwd"]


def parse_log_line(line):
    """Mengurai 1 baris log mentah menjadi dictionary terstruktur."""
    match = re.search(LOG_PATTERN, line)
    if match:
        return {
            "ip": match.group(1),
            "timestamp": match.group(2),
            "method": match.group(3),
            "url": match.group(4),
            "status_code": int(match.group(5)),
            "size": int(match.group(6)),
        }
    return None


def detect_brute_force(parsed_logs, threshold=3):
    """Mendeteksi IP yang melakukan percobaan login gagal melebihi batas threshold."""
    failed_attempts = defaultdict(int)

    for log in parsed_logs:
        if "/login" in log["url"] and log["status_code"] == 401:
            failed_attempts[log["ip"]] += 1

    alerts = []
    for ip, count in failed_attempts.items():
        if count >= threshold:
            alerts.append({
                "ip": ip,
                "type": "Brute Force Login Attempt",
                "details": (
                    f"Terdeteksi {count} kali percobaan login gagal pada /login"
                ),
                "severity": "HIGH",
            })
    return alerts


def detect_web_attacks(parsed_logs):
    """Mendeteksi muatan serangan SQL Injection dan Path Traversal pada URL."""
    alerts = []

    for log in parsed_logs:
        url = log["url"]

        # 1. Cek SQL Injection
        for pattern in SQLI_PATTERNS:
            if re.search(pattern, url, re.IGNORECASE):
                alerts.append({
                    "ip": log["ip"],
                    "type": "SQL Injection (SQLi)",
                    "details": f"Payload terdeteksi pada URL: {url}",
                    "severity": "HIGH",
                })
                break

        # 2. Cek Path Traversal
        for pattern in PATH_TRAVERSAL_PATTERNS:
            if re.search(pattern, url, re.IGNORECASE):
                alerts.append({
                    "ip": log["ip"],
                    "type": "Directory / Path Traversal",
                    "details": f"Akses file sensitif terdeteksi: {url}",
                    "severity": "HIGH",
                })
                break

    return alerts


def export_to_json(alerts, filename="incident_report.json"):
    """Menyimpan daftar ancaman ke dalam berkas JSON."""
    try:
        with open(filename, "w") as json_file:
            json.dump(alerts, json_file, indent=4)
        print(f"[+] Berhasil mengekspor laporan insiden ke file: '{filename}'")
    except Exception as e:
        print(f"[-] Gagal mengekspor file JSON: {e}")


def main():
    log_file_path = "access.log"
    parsed_logs = []

    print("=" * 70)
    print(" 🛡️ SECURITY MONITORING & INCIDENT DETECTION ENGINE (v2)")
    print("=" * 70)

    # Membaca Log
    try:
        with open(log_file_path, "r") as file:
            for line in file:
                parsed_data = parse_log_line(line.strip())
                if parsed_data:
                    parsed_logs.append(parsed_data)
    except FileNotFoundError:
        print(f"[-] ERROR: File '{log_file_path}' tidak ditemukan.")
        return

    print(f"[+] Total log berhasil diurai: {len(parsed_logs)} baris\n")

    # Jalankan Mesin Deteksi
    brute_force_alerts = detect_brute_force(parsed_logs)
    web_attack_alerts = detect_web_attacks(parsed_logs)
    all_alerts = brute_force_alerts + web_attack_alerts

    # Tampilkan Laporan di Terminal
    print("🚨 LAPORAN DETEKSI ANCAMAN KEAMANAN (INCIDENT REPORT):")
    print("-" * 70)

    if all_alerts:
        for idx, alert in enumerate(all_alerts, 1):
            print(f"[{idx}] TINGKAT RISIKO : {alert['severity']}")
            print(f"    ALAMAT IP      : {alert['ip']}")
            print(f"    JENIS SERANGAN : {alert['type']}")
            print(f"    KETERANGAN     : {alert['details']}")
            print("-" * 70)

        # Ekspor laporan ke file JSON
        export_to_json(all_alerts)
    else:
        print("[+] Tidak terdeteksi ancaman keamanan pada berkas log.")


if __name__ == "__main__":
    main()