# SCHEMA.md — Struktur Data

## Google Sheet — Senarai Saham

### Nama Sheet yang Disyorkan
`Stock_List` (atau mana-mana nama, boleh dikonfigurasi dalam `config`)

### Struktur Lajur

| Lajur | Nama Header | Jenis Data | Contoh Nilai | Keterangan |
|-------|-------------|------------|--------------|------------|
| **A** | `Stock_Name` | String | `Maybank` | Nama mesra untuk dipaparkan dalam dropdown UI |
| **B** | `Ticker_Code` | String | `1155.KL` | Kod ticker yang digunakan oleh yfinance untuk cari data |

### Peraturan Ticker Code

> ⚠️ **Wajib**: Ticker untuk saham pasaran tempatan (Bursa Malaysia) **mesti** menggunakan suffix `.KL`
> supaya `yfinance` dapat mengenalinya dengan betul.

| Pasaran | Format | Contoh |
|---------|--------|--------|
| Bursa Malaysia | `{Nombor}.KL` | `1155.KL`, `1023.KL`, `5347.KL` |
| US Market (NYSE/NASDAQ) | `{Simbol}` | `AAPL`, `TSLA`, `MSFT` |
| Singapore (SGX) | `{Simbol}.SI` | `D05.SI`, `O39.SI` |
| Hong Kong (HKEX) | `{Nombor}.HK` | `0700.HK`, `9988.HK` |

### Contoh Data dalam Google Sheet

```
| A (Stock_Name)      | B (Ticker_Code) |
|---------------------|-----------------|
| Maybank             | 1155.KL         |
| CIMB Group          | 1023.KL         |
| Public Bank         | 1295.KL         |
| Tenaga Nasional     | 5347.KL         |
| IHH Healthcare      | 5225.KL         |
| Petronas Chemicals  | 5183.KL         |
| Top Glove           | 7113.KL         |
| Axiata Group        | 6888.KL         |
```

### Peraturan Pengisian Sheet

1. **Baris pertama adalah header** — `Stock_Name` dan `Ticker_Code`
2. **Tiada baris kosong** di antara data (boleh menyebabkan senarai dropdown tidak lengkap)
3. **Tiada ruang tersembunyi** (trailing spaces) pada Ticker_Code
4. **Huruf besar/kecil** pada suffix `.KL` tidak kritikal, tetapi amalan terbaik adalah huruf besar

---

## Struktur Data Dalaman (In-Memory)

### DataFrame Senarai Saham (dari Google Sheet)

```python
# Contoh struktur pandas DataFrame selepas dibaca dari Sheet
df_stocks = pd.DataFrame({
    "Stock_Name":   ["Maybank", "CIMB Group", "Public Bank"],
    "Ticker_Code":  ["1155.KL", "1023.KL",    "1295.KL"]
})
```

### DataFrame OHLCV (dari yfinance)

```python
# Contoh struktur pandas DataFrame selepas ditarik dari yfinance
# Index: DatetimeIndex
df_ohlcv = pd.DataFrame({
    "Open":   [8.50, 8.55, 8.48],
    "High":   [8.62, 8.70, 8.55],
    "Low":    [8.45, 8.50, 8.40],
    "Close":  [8.60, 8.65, 8.52],
    "Volume": [12500000, 9800000, 11200000]
}, index=pd.DatetimeIndex(["2026-07-28", "2026-07-29", "2026-07-30"]))
```

### DataFrame dengan Indikator (selepas pandas-ta)

```python
# Lajur tambahan selepas pengiraan indikator
df_with_indicators = df_ohlcv.copy()
df_with_indicators["SMA_20"]        # Simple Moving Average 20 hari
df_with_indicators["SMA_50"]        # Simple Moving Average 50 hari
df_with_indicators["RSI_14"]        # Relative Strength Index 14 hari
df_with_indicators["MACD_12_26_9"]  # MACD line
df_with_indicators["MACDs_12_26_9"] # Signal line
df_with_indicators["MACDh_12_26_9"] # Histogram
```

---

## Konfigurasi Sambungan Google Sheet

Maklumat berikut perlu dikonfigurasi dalam `.streamlit/secrets.toml`:

```toml
[gcp_service_account]
type = "service_account"
project_id = "YOUR_PROJECT_ID"
private_key_id = "YOUR_KEY_ID"
private_key = "-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----\n"
client_email = "YOUR_SERVICE_ACCOUNT@YOUR_PROJECT.iam.gserviceaccount.com"
client_id = "YOUR_CLIENT_ID"

[google_sheet]
spreadsheet_url = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit"
worksheet_name = "Stock_List"
```
