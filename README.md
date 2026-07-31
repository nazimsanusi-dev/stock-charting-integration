# 📈 Stock Monitor

Aplikasi web ringan untuk memantau pergerakan harga saham Malaysia (Bursa) dan global — tanpa bergantung pada TradingView atau Moomoo.

**Dibina dengan:** Python · Streamlit · Plotly · yfinance · gspread

---

## Ciri-ciri

- 📋 Senarai saham diuruskan terus dari **Google Sheet**
- 🕯️ **Carta Candlestick** interaktif (zoom, hover, pan)
- 📐 Indikator teknikal: **SMA 20/50**, **RSI 14**, **MACD**
- ⚡ Caching automatik — aplikasi pantas walaupun data banyak

---

## Struktur Projek

```
stock-charting-integration/
├── app.py                          # Titik masuk Streamlit
├── requirements.txt                # Kebergantungan Python
├── data/
│   ├── sheet_loader.py             # Baca Google Sheet (gspread)
│   └── stock_fetcher.py            # Tarik data harga (yfinance)
├── logic/
│   └── indicators.py               # Kira SMA, RSI, MACD (pandas-ta)
├── ui/
│   ├── sidebar.py                  # Komponen sidebar
│   └── chart.py                    # Bina carta Plotly
└── .streamlit/
    └── secrets.toml.template       # Contoh konfigurasi (isi & simpan sebagai secrets.toml)
```

---

## Persediaan Tempatan (Local Setup)

### 1. Install kebergantungan

```bash
pip install -r requirements.txt
```

### 2. Sediakan Google Service Account

1. Pergi ke [Google Cloud Console](https://console.cloud.google.com/)
2. Buat projek baharu → aktifkan **Google Sheets API** dan **Google Drive API**
3. Buat **Service Account** → Cipta kunci JSON
4. **Kongsi** Google Sheet anda dengan emel Service Account (`...@....iam.gserviceaccount.com`)

### 3. Sediakan fail secrets

Salin template dan isi dengan kelayakan sebenar:

```bash
cp .streamlit/secrets.toml.template .streamlit/secrets.toml
# Edit .streamlit/secrets.toml dengan teks editor pilihan anda
```

> ⚠️ **Jangan commit** `.streamlit/secrets.toml` — ia sudah ada dalam `.gitignore`

### 4. Sediakan Google Sheet

Buat Google Sheet dengan nama lembaran `Stock_List` dan struktur berikut:

| A (Stock_Name) | B (Ticker_Code) |
|----------------|-----------------|
| Maybank        | 1155.KL         |
| CIMB Group     | 1023.KL         |

> Saham Bursa Malaysia **mesti** ada suffix `.KL`

### 5. Jalankan aplikasi

```bash
streamlit run app.py
```

---

## 🚀 Deploy ke Streamlit Community Cloud (Percuma)

### Langkah 1 — Push ke GitHub

Pastikan semua fail sudah di-commit dan push ke repositori GitHub anda:

```bash
git add .
git commit -m "Initial project setup"
git push origin main
```

> ⚠️ Pastikan `.streamlit/secrets.toml` **tidak** di-push (ia sudah dilindungi dalam `.gitignore`)

### Langkah 2 — Log masuk ke Streamlit Cloud

Pergi ke **[share.streamlit.io](https://share.streamlit.io)** dan log masuk menggunakan akaun GitHub anda.

### Langkah 3 — Sambung repositori

1. Klik **"New app"**
2. Pilih repositori GitHub anda
3. Pilih branch: `main`
4. Set main file path: `app.py`

### Langkah 4 — Tetapkan Secrets ⚠️ (Penting)

Sebelum klik Deploy:

1. Klik **"Advanced settings"**
2. Di bahagian **Secrets**, tampal kandungan penuh `secrets.toml` anda (dengan kelayakan Service Account sebenar)

```toml
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "..."
private_key = "-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----\n"
client_email = "your-sa@your-project.iam.gserviceaccount.com"
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"

[google_sheet]
spreadsheet_url = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit"
worksheet_name = "Stock_List"
```

### Langkah 5 — Deploy

Klik **"Deploy"**. Streamlit akan membina aplikasi anda dan memberikan URL awam seperti:

```
https://your-app-name.streamlit.app
```

---

## Rujukan Dokumen

| Dokumen | Kandungan |
|---------|-----------|
| [PRD.md](PRD.md) | Keperluan produk dan skop |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Seni bina sistem dan tech stack |
| [DESIGN.md](DESIGN.md) | Reka bentuk UI dan palet warna |
| [SCHEMA.md](SCHEMA.md) | Struktur Google Sheet dan data |
| [RULES.md](RULES.md) | Peraturan kod dan prestasi |
