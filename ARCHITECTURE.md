# ARCHITECTURE.md — Seni Bina Sistem

## Gambaran Keseluruhan

Aplikasi ini dibina sepenuhnya menggunakan **Python** dengan seni bina berlapis yang memisahkan tanggungjawab data, logik, dan paparan.

```
┌─────────────────────────────────────────────┐
│                  PENGGUNA                   │
│              (Web Browser)                  │
└───────────────────┬─────────────────────────┘
                    │
┌───────────────────▼─────────────────────────┐
│             LAPISAN PAPARAN                 │
│                Streamlit                    │
│   (UI, sidebar, carta, interaktiviti)       │
└───────────────────┬─────────────────────────┘
                    │
┌───────────────────▼─────────────────────────┐
│              LAPISAN LOGIK                  │
│           pandas + pandas-ta                │
│  (pengiraan SMA, RSI, MACD, transformasi)   │
└──────────┬────────────────────┬─────────────┘
           │                    │
┌──────────▼──────┐   ┌─────────▼─────────────┐
│  SUMBER DATA 1  │   │    SUMBER DATA 2       │
│  Google Sheets  │   │    Yahoo Finance       │
│    (gspread)    │   │     (yfinance)         │
└─────────────────┘   └───────────────────────┘
```

## Tindanan Teknologi (Tech Stack)

| Lapisan | Teknologi | Tujuan |
|---------|-----------|--------|
| **Bahasa** | Python 3.10+ | Bahasa utama |
| **UI / Paparan** | Streamlit | Antara muka web tanpa perlu HTML/CSS |
| **Carta** | Plotly | Carta interaktif candlestick |
| **Data Saham** | yfinance | Tarik data OHLCV dari Yahoo Finance |
| **Google Sheet** | gspread | Baca senarai saham dari Google Sheet |
| **Auth Google** | google-auth | Pengesahan menggunakan Service Account |
| **Pengiraan** | pandas | Manipulasi dan analisis data |
| **Indikator** | pandas-ta | Pengiraan indikator teknikal (SMA, RSI, MACD) |

## Aliran Data (Data Flow)

```
1. App bermula
   → Streamlit memuatkan konfigurasi

2. Ambil senarai saham
   → gspread membaca Google Sheet
   → Senarai {Stock_Name: Ticker_Code} dimuatkan ke dropdown
   → Hasil di-cache dengan @st.cache_data

3. Pengguna pilih saham
   → yfinance menarik data OHLCV berdasarkan Ticker_Code
   → Hasil di-cache dengan @st.cache_data

4. Pengiraan indikator
   → pandas-ta mengira SMA, RSI, MACD dari data OHLCV

5. Paparan carta
   → Plotly membina carta candlestick + indikator
   → Streamlit memaparkan carta kepada pengguna
```

## Struktur Fail Projek

```
stock-charting-integration/
├── app.py                  # Titik masuk utama Streamlit
├── data/
│   ├── sheet_loader.py     # Fungsi baca Google Sheet (gspread)
│   └── stock_fetcher.py    # Fungsi tarik data harga (yfinance)
├── logic/
│   └── indicators.py       # Pengiraan SMA, RSI, MACD (pandas-ta)
├── ui/
│   ├── sidebar.py          # Komponen sidebar (dropdown, checkbox)
│   └── chart.py            # Pembinaan carta Plotly
├── config/
│   └── credentials.json    # Google Service Account key (JANGAN commit)
├── requirements.txt        # Senarai kebergantungan Python
└── .streamlit/
    └── secrets.toml        # Konfigurasi rahsia Streamlit (JANGAN commit)
```

## Kebergantungan (requirements.txt)

```
streamlit
plotly
yfinance
gspread
google-auth
pandas
pandas-ta
```
