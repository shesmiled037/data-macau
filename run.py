import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import requests

# Load .env
load_dotenv()
WP_API_URL = os.getenv("WP_API_URL")
WP_USER = os.getenv("WP_USER")
WP_PASS = os.getenv("WP_PASS")

def ambil_tabel_macau():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("http://146.190.92.226/", timeout=30000, wait_until="domcontentloaded")
            page.wait_for_selector("table.baru", timeout=10000)
            html = page.content()
            browser.close()

            soup = BeautifulSoup(html, "html.parser")
            tabel_list = soup.find_all("table", class_="baru")

            if not tabel_list:
                print("❌ Tidak ada tabel ditemukan.")
                return None

            hasil = []

            for table in tabel_list:
                # Ambil heading sebelum tabel
                heading = table.find_previous(["h2", "h3", "h4"])
                if heading:
                    hasil.append(f"<{heading.name}>{heading.text.strip()}</{heading.name}>")

                # Hapus baris tak berguna
                for row in table.find_all("tr"):
                    first_td = row.find("td")
                    if first_td and "/" not in first_td.text:
                        row.decompose()

                # Tambahkan thead custom
                custom_header = """
                <thead>
                <tr>
                <th rowspan="2" style="background-color:#0f358c !important; color:#fcf800 !important; padding:8px; text-align:center;">TANGGAL</th>
                <th colspan="6" style="background-color:#0f358c !important; color:#fcf800 !important; padding:8px; text-align:center;">Data Macau 2025 Terbaru</th>
                </tr>
                <tr>
                <th style="background-color:#0f358c !important; color:#fcf800 !important; padding:8px; text-align:center;">13:00</th>
                <th style="background-color:#0f358c !important; color:#fcf800 !important; padding:8px; text-align:center;">16:00</th>
                <th style="background-color:#0f358c !important; color:#fcf800 !important; padding:8px; text-align:center;">19:00</th>
                <th style="background-color:#0f358c !important; color:#fcf800 !important; padding:8px; text-align:center;">22:00</th>
                <th style="background-color:#0f358c !important; color:#fcf800 !important; padding:8px; text-align:center;">23:00</th>
                <th style="background-color:#0f358c !important; color:#fcf800 !important; padding:8px; text-align:center;">24:00</th>
                </tr>
                </thead>
                    """

                tbody = table.find("tbody")
                if not tbody:
                    tbody = soup.new_tag("tbody")
                    tbody.extend(table.find_all("tr"))
                    table.clear()
                    table.append(tbody)
                table.insert(0, BeautifulSoup(custom_header, "html.parser"))

                # Hapus warna lama (optional, biar konsisten)
                table_html = str(table).replace("#68a225", "").replace("#265c00", "")
                hasil.append(table_html)

            print(f"✅ Ditemukan {len(tabel_list)} tabel + judul.")
            return "\n".join(hasil)

    except Exception as e:
        print(f"❌ Error ambil data: {e}")
        return None

def gabungkan_ke_template(tabel_html):
    try:
        bagian_atas = """
<article id="post-4660" class="single-view post-4660 page type-page status-publish hentry">
<div class="entry-byline cf">
  <header class="entry-header cf">
    <h1 class="entry-title" itemprop="headline"><a href="./">Data Keluaran Macau 2025</a></h1>
  </header>
</div>

<div class="entry-content cf" itemprop="text">
  <p><strong>Data Keluaran Macau 2025, Data Toto macau 2025, Pengeluaran Macau Pools4d Terlengkap</strong></p>
  <p>Rekap Pengeluaran Togel Macau pools terbaru, result macau malam ini tercepat, paito toto macau 2025 tercepat. Hasil Keluaran macau prize lengkap, Result macau harian, pengeluaran toto macau terakurat dan resmi yang berasal dari website resmi <strong>totomacaupools.asia</strong>.</p>
  <p><span style="text-decoration: underline;"><strong>Data Macau  2025</strong>&nbsp;</span>dapat kamu pergunakan dalam melakukan pencarian angka tarikan paito macau untuk mendapatkan nomor terbaik yang di pasang nantinya.</p>
  <div id="attachment_4664" style="width: 1010px" class="wp-caption aligncenter"><p id="caption-attachment-4664" class="wp-caption-text">Data Keluaran Macau 2025, Pengeluaran Toto Macau Hari Ini</p></div>
  <table>
    <tbody>
      <tr>
        <td>Pasaran Toto macau Aktif Setiap hari dan untuk <em><strong>result pengeluaran macau</strong></em> keluar pada pukul 13.00 Wib, 16.00 Wib, 19.00 Wib, 22.00 Wib dan pukul 24.00 WIB langsung dari <strong>totomacaupools.asia</strong></td>
      </tr>
    </tbody>
  </table>
"""

        bagian_bawah = """
  <p><strong>Data Keluaran Macau 2025</strong>&nbsp;sangat bagus dalam mencari angka tarikan paito, pergunakan data toto macau terlengkap ini dalam bermain togel.</p>
  <h3>Data Keluaran Macau 2025</h3>
  <p>Tabel <a href="./"><span style="text-decoration: underline;"><strong>Data keluaran macau 2025</strong></span></a> yang kami tampilkan dalam tabel di atas merupakan hasil yang sudah sah. Result Macau hari ini, Data pengeluaran toto macau tercepat, Angka keluar macau malam ini dapat langsung di lihat di website datakeluaran.org ini.</p>
</div>
<footer class="entry-footer cf"></footer>
</article>
"""

        hasil_html = bagian_atas + tabel_html + bagian_bawah

        with open("result_macau.html", "w", encoding="utf-8") as f:
            f.write(hasil_html)

        print("✅ result_macau.html berhasil dibuat.")
        return hasil_html
    except Exception as e:
        print(f"❌ Error saat gabung template: {e}")
        return None

def post_ke_wordpress(html_content):
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
            print("✅ Berhasil posting ke WordPress.")
            print(f"🔗 Link: {r.json().get('link')}")
        else:
            print(f"❌ Gagal post: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"❌ Error saat post ke WordPress: {e}")

if __name__ == "__main__":
    tabel_html = ambil_tabel_macau()
    if tabel_html:
        full_html = gabungkan_ke_template(tabel_html)
        if full_html:
            post_ke_wordpress(full_html)
