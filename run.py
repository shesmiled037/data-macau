import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

# Load variabel dari .env
load_dotenv()
WP_API_URL = os.getenv("WP_API_URL")  # endpoint untuk POST
WP_USER = os.getenv("WP_USER")
WP_PASS = os.getenv("WP_PASS")

def ambil_tabel_dari_situs():
    try:
        url = "http://146.190.92.226/"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        tabel_list = soup.find_all("table")
        if not tabel_list:
            print("❌ Tidak ada tabel ditemukan.")
            return None
        return "\n".join(str(tbl) for tbl in tabel_list)
    except Exception as e:
        print(f"❌ Gagal ambil data: {e}")
        return None

def gabungkan_ke_template(tabel_html):
    try:
        with open("ini.txt", "r", encoding="utf-8") as f:
            template = f.read()

        hasil_html = template.replace("{{TABEL_MACAU}}", tabel_html)

        # Ganti warna tabel
        hasil_html = hasil_html.replace("#68a225", "#29bfe5")  # hijau muda → biru muda
        hasil_html = hasil_html.replace("#265c00", "#30257d")  # hijau tua → ungu gelap

        with open("result_macau.html", "w", encoding="utf-8") as f:
            f.write(hasil_html)

        print("✅ result_macau.html berhasil dibuat.")
        return hasil_html

    except Exception as e:
        print("❌ Error gabung template:", e)
        return None


def post_ke_wordpress_as_post(html_content):
    if not WP_API_URL or not WP_USER or not WP_PASS:
        print("❌ Data .env tidak lengkap.")
        return

    headers = {"Content-Type": "application/json"}
    data = {
        "title": "",
        "content": html_content,
        "status": "publish"
    }

    try:
        r = requests.post(WP_API_URL, json=data, auth=(WP_USER, WP_PASS), headers=headers)
        if r.status_code in [200, 201]:
            print("✅ Berhasil posting ke WordPress (post).")
            print(f"🔗 Link: {r.json().get('link')}")
        else:
            print(f"❌ Gagal post: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"❌ Error saat post ke WordPress: {e}")

if __name__ == "__main__":
    tabel_html = ambil_tabel_dari_situs()
    if tabel_html:
        full_html = gabungkan_ke_template(tabel_html)
        if full_html:
            with open("result_macau.html", "w", encoding="utf-8") as f:
                f.write(full_html)
            print("✅ File result_macau.html disimpan.")
            post_ke_wordpress_as_post(full_html)
