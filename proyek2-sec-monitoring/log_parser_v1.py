import re

# Pola regex untuk mencocokkan pola Nginx/Apache access log
LOG_PATTERN = r'(\d+\.\d+\.\d+\.\d+)\s+-\s+-\s+\[(.*?)\]\s+"(\w+)\s+(.*?)\s+HTTP/.*?"\s+(\d+)\s+(\d+)'

def parse_log_line(line):
    """
    Mengurai 1 baris teks mentah log menjadi dictionary terstruktur
    """
    match = re.search(LOG_PATTERN, line)
    if match:
        return {
            "ip": match.group(1),
            "timestamp": match.group(2),
            "method": match.group(3),
            "url": match.group(4),
            "status_code": match.group(5),
            "size": match.group(6)
        }
    return None

def main():
    log_file_path = "access.log"
    parsed_log = []

    print("=" * 65)
    print("        🔍 LOG PARSER ENGINE (PROYEK 2 - SEC MONITORING)")
    print("=" * 65)

    try:
        with open(log_file_path, "r") as file:
            for line_number, line in enumerate(file, 1):
                parsed_data = parse_log_line(line.strip())
                if parsed_data:
                    parsed_log.append(parsed_data)
                else:
                    print(f"[!] Gagal mengurai baris {line_number}: {line.strip()}")
        
        print(f"\n[+] Berhasil mengurai {len(parsed_log)} baris log dari '{log_file_path}'\n")
        print(f"{'IP ADDRESS':<16} | {'METHOD':<6} | {'STATUS':<6} | {'URL / ENDPOINT'}")
        print("-" * 65)

        # Mencetak hasil parse ke layar
        for log in parsed_log:
            print(f"{log['ip']:<16} | {log['method']:<6} | {log['status_code']:<6} | {log['url']}")

    except FileNotFoundError:
        print(f"[-] ERROR: Berkas '{log_file_path}' tidak ditemukan. Pastikan file access.log sudah dibuat.")

if __name__ == "__main__":
    main()