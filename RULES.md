# RULES.md — Peraturan Pembangunan

## 1. Prestasi (Performance)

### Wajib Gunakan Caching

Semua fungsi yang membuat panggilan rangkaian luaran **mesti** menggunakan `@st.cache_data`.

```python
# ✅ BETUL — dengan caching
@st.cache_data(ttl=3600)  # cache selama 1 jam
def load_stock_list():
    """Baca senarai saham dari Google Sheet."""
    ...

@st.cache_data(ttl=900)  # cache selama 15 minit
def fetch_stock_data(ticker: str, period: str):
    """Tarik data OHLCV dari Yahoo Finance."""
    ...

# ❌ SALAH — tanpa caching (aplikasi akan jadi lambat)
def load_stock_list():
    ...
```

### Panduan TTL (Time-To-Live) Cache

| Fungsi | TTL | Sebab |
|--------|-----|-------|
| `load_stock_list()` | `3600s` (1 jam) | Senarai saham jarang berubah |
| `fetch_stock_data()` | `900s` (15 minit) | Data harga tidak perlu real-time |

---

## 2. Standard Kod (Code Standards)

### Pemisahan Tanggungjawab (Separation of Concerns)

Kod **mesti** diasingkan mengikut lapisan fungsi:

```
✅ STRUKTUR YANG BETUL:

data/sheet_loader.py    → Semua logik baca Google Sheet
data/stock_fetcher.py   → Semua logik tarik data yfinance
logic/indicators.py     → Semua pengiraan indikator teknikal
ui/sidebar.py           → Semua komponen sidebar Streamlit
ui/chart.py             → Semua pembinaan carta Plotly
app.py                  → Titik masuk, panggil modul di atas sahaja
```

```python
# ❌ SALAH — semua bercampur dalam satu fungsi
def render_page():
    gc = gspread.authorize(...)
    df = gc.open_by_url(...).get_all_records()
    data = yf.download(...)
    data.ta.sma(length=20, append=True)
    fig = go.Figure(...)
    st.plotly_chart(fig)

# ✅ BETUL — setiap lapisan diasingkan
def render_page():
    stocks = load_stock_list()          # data layer
    ohlcv = fetch_stock_data(ticker)    # data layer
    ohlcv = calculate_indicators(ohlcv) # logic layer
    fig = build_chart(ohlcv)            # ui layer
    st.plotly_chart(fig)                # presentation
```

### Konvensyen Penamaan

| Jenis | Konvensyen | Contoh |
|-------|-----------|--------|
| Fungsi | `snake_case` | `fetch_stock_data()` |
| Pemboleh ubah | `snake_case` | `ticker_code`, `df_ohlcv` |
| Pemalar | `UPPER_SNAKE_CASE` | `DEFAULT_PERIOD`, `CACHE_TTL` |
| Fail | `snake_case.py` | `sheet_loader.py` |
| Kelas | `PascalCase` | `StockData` |

### Type Hints

Semua fungsi **mesti** menggunakan type hints:

```python
# ✅ BETUL
def fetch_stock_data(ticker: str, period: str = "3mo") -> pd.DataFrame:
    ...

# ❌ SALAH
def fetch_stock_data(ticker, period):
    ...
```

---

## 3. Keselamatan (Security)

- **Jangan sekali-kali** commit `credentials.json` atau `.streamlit/secrets.toml` ke Git
- Tambah ke `.gitignore`:
  ```
  config/credentials.json
  .streamlit/secrets.toml
  ```
- Gunakan environment variables atau Streamlit Secrets untuk semua nilai sensitif

---

## 4. Pengendalian Ralat (Error Handling)

```python
# ✅ Sentiasa tangani kes di mana data tidak tersedia
@st.cache_data(ttl=900)
def fetch_stock_data(ticker: str, period: str) -> pd.DataFrame | None:
    try:
        df = yf.download(ticker, period=period)
        if df.empty:
            return None
        return df
    except Exception as e:
        st.error(f"Gagal mendapatkan data untuk {ticker}: {e}")
        return None

# Dalam UI, semak nilai None sebelum papar carta
data = fetch_stock_data(ticker, period)
if data is None:
    st.warning("Data tidak tersedia untuk saham ini.")
    st.stop()
```

---

## 5. Senarai Semak Sebelum Deploy

- [ ] `@st.cache_data` dipasang pada semua fungsi data
- [ ] `credentials.json` dan `secrets.toml` ada dalam `.gitignore`
- [ ] Semua fungsi mempunyai type hints
- [ ] Backend (data/logik) dan frontend (UI) diasingkan
- [ ] Error handling ditambah untuk semua panggilan luaran
- [ ] `requirements.txt` dikemas kini dengan semua kebergantungan
