Berikut adalah **Laporan Analisis Keamanan Eksekutif** dan rekomendasi mitigasi insiden berdasarkan log yang terdeteksi:

---

# **LAPORAN ANALISIS KEAMANAN SIBER & INSIDEN RESPONSE**
**Klasifikasi:** SANGAT RAHASIA (Internal Only)  
**Status Penanganan:** Active Incident  
**Disusun Oleh:** Senior SOC Security Analyst & Incident Response Specialist  

---

### **1. Ringkasan Insiden (Executive Summary)**
Telah terdeteksi aktivitas anomali berkategori risiko tinggi (*High Severity*) pada server aplikasi web. Terdapat upaya eksploitasi multi-vektor secara bersamaan:
1. Serangan **Brute Force** terhadap endpoint autentikasi (`/login`) oleh IP `10.0.0.99`.
2. Serangan **SQL Injection (SQLi)** dan **Directory/Path Traversal** terkoordinasi oleh IP `172.16.0.12`.

Kedua alamat IP penyerang berada pada blok IP privat (*Private IP Address* / RFC 1918), yang mengindikasikan adanya potensi **ancaman dari dalam (*Insider Threat*)** atau **host internal yang telah berhasil disusupi (*Compromised Host*)** dan dijadikan batu loncatan (*Lateral Movement*) oleh aktor ancaman. Jika tidak ditangani segera, ancaman ini dapat menyebabkan kebocoran data sensitif (*data breach*), pengambilalihan akun pengguna, hingga kompromi penuh terhadap sistem operasi server.

---

### **2. Analisis Akar Masalah (Root Cause Analysis)**

#### **A. Brute Force Login Attempt (IP: `10.0.0.99`)**
* **Mekanisme Serangan:** Penyerang mengirimkan kredensial tebakan berulang kali ke `/login`.
* **Akar Masalah (*Root Cause*):** Tidak adanya mekanisme pembatasan frekuensi percobaan (*Rate Limiting*), kebijakan penguncian akun (*Account Lockout Policy*), atau proteksi bot (CAPTCHA) pada endpoint autentikasi.
* **Dampak:** Potensi pengambilalihan akun (*Account Takeover*) dan penipisan sumber daya server (*Resource Exhaustion*).

#### **B. SQL Injection / SQLi (IP: `172.16.0.12`)**
* **Payload:** `/products.php?id=1%27%20OR%201=1--`
* **Mekanisme Serangan:** Tautologi logika Boolean (`' OR 1=1--`). Penyerang berusaha memanipulasi kueri SQL agar selalu bernilai *TRUE* dan mengabaikan sisa sintaks kueri asli dengan tanda komentar (`--`).
* **Akar Masalah (*Root Cause*):** Parameter `id` pada `products.php` digabungkan secara dinamis (*string concatenation*) langsung ke dalam kueri database tanpa sanitasi, validasi tipe data, atau *Prepared Statements*.
* **Dampak:** Pembacaan data sensitif yang tidak sah (*Data Exfiltration*), bypass autentikasi, integritas data rusak, atau eksekusi perintah OS (jika hak akses database terlalu tinggi, misal `xp_cmdshell` / `LOAD_FILE`).

#### **C. Directory / Path Traversal (IP: `172.16.0.12`)**
* **Payload:** `/../../etc/passwd`
* **Mekanisme Serangan:** Penggunaan karakter manipulasi direktori (`../`) untuk keluar dari *root web directory* (*DocumentRoot*) dan mengakses berkas sistem operasi.
* **Akar Masalah (*Root Cause*):** Penanganan berkas (*file retrieval*) menggunakan *user-input* secara mentah tanpa kanonisasi (*canonicalization*) atau validasi *whitelist* terhadap path file.
* **Dampak:** *Information Disclosure* tingkat OS (pembacaan `/etc/passwd` membocorkan daftar akun pengguna lokal, shell sistem, dan struktur user Linux) yang menjadi bekal untuk *Privilege Escalation*.

---

### **3. Rencana Mitigasi Taktis (Actionable Remediation Plan)**

#### **Fase 1: Tindakan Cepat & Isolasi (Immediate Tactical Containment)**
1. **Blokir & Karantina Host:**
   * Terapkan *Temporary Block* pada Web Application Firewall (WAF) / Firewall OS (`iptables` / `nftables`) untuk IP `172.16.0.12` dan `10.0.0.99`:
     ```bash
     sudo iptables -A INPUT -s 172.16.0.12 -j DROP
     sudo iptables -A INPUT -s 10.0.0.99 -j DROP
     ```
   * Isolasi workstation/perangkat yang menggunakan kedua IP tersebut dari jaringan utama untuk investigasi forensik malware/insider.
2. **Audit Dampak Serangan (*Post-Exploitation Check*):**
   * Periksa log akses web server: Cek *HTTP Response Code* terhadap payload `/../../etc/passwd` dan `products.php`.
     * Jika merespons **200 OK** dengan payload size besar: **Asumsikan data sudah bocor**. Segera jalankan prosedur *Incident Response Escalation*.
3. **Aktifkan Rule WAF Sementara:**
   * Aktifkan OWASP Core Rule Set (CRS) untuk modul SQLi (Rule 942xxx) dan Path Traversal (Rule 930xxx).

#### **Fase 2: Perbaikan Kode & Pengerasan Sistem (Permanent Remediation)**

* **Perbaikan SQL Injection:**
  * Wajib gunakan **Parameterized Queries / Prepared Statements** (contoh PHP PDO):
    ```php
    // PERBAIKAN: Gunakan Prepared Statements
    $stmt = $pdo->prepare('SELECT * FROM products WHERE id = :id');
    $stmt->execute(['id' => $id]);
    $product = $stmt->fetch();
    ```
  * Pastikan validasi tipe data input (contoh: pastikan `id` harus berupa integer: `intval($_GET['id'])`).

* **Perbaikan Path Traversal:**
  * Jangan gunakan input langsung dari URL untuk memuat file lokal.
  * Gunakan fungsi `basename()` dan `realpath()` untuk mencegah manipulasi direktori, atau gunakan sistem indeks (*ID mapping* berbasis database):
    ```php
    $filename = basename($_GET['file']);
    $filepath = '/var/www/uploads/' . $filename;
    // Validasi apakah path yang dituju tetap di dalam folder aman
    if (strpos(realpath($filepath), '/var/www/uploads/') !== 0) {
        die('Akses ditolak!');
    }
    ```
  * Terapkan prinsip *Least Privilege* pada web server user (`www-data`/`nginx`) agar tidak memiliki akses baca ke `/etc/passwd` atau file sensitif sistem lainnya.

* **Perbaikan Brute Force:**
  * **Rate Limiting:** Batasi maksimal 5 percobaan login gagal per IP/akun dalam jendela waktu 5 menit (menggunakan Redis / Nginx `limit_req_zone`).
  * **MFA & CAPTCHA:** Terapkan Cloudflare Turnstile / Google reCAPTCHA pada formulir `/login` dan wajibkan Multi-Factor Authentication (MFA) bagi akun kritikal.

---

### **4. Tingkat Urgensi Response**

### **PRIORITAS: CRITICAL (P1)**

**Alasan Justifikasi:**
1. **Vektor Serangan Internal:** Serangan berasal dari IP privat. Ini menandakan adanya penyerang yang sudah berada di dalam perimeter jaringan lokal (*perimeter breach*).
2. **Kombinasi Serangan Berbahaya:** Penyerang IP `172.16.0.12` secara agresif mencoba membaca file sensitif OS dan mengeksploitasi basis data secara simultan. Eksploitasi sukses dapat berujung pada kendali penuh atas server (*Full System Compromise*).

**Target SLA Response:** Isolasi IP dan penahanan (*containment*) wajib diselesaikan dalam kurun waktu **kurang dari 1 jam** sejak laporan ini diterbitkan.