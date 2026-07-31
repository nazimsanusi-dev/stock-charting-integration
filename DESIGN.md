# DESIGN.md — Reka Bentuk UI/UX

## Falsafah Reka Bentuk

> **Minimalis, kemas, dan bersih** — terinspirasi daripada estetika Muji.
> Kurang gangguan, lebih fokus kepada data.

### Prinsip Utama

- **Putih dan ruang kosong** mendominasi untuk ketenangan visual
- **Tipografi bersih** tanpa hiasan berlebihan
- **Warna berfungsi** — hanya digunakan untuk menyampaikan makna (merah = turun, hijau = naik)
- **Interaktiviti halus** — zoom, hover, dan toggle tanpa rasa terlalu "sibuk"

---

## Susun Atur (Layout)

```
┌──────────────────────────────────────────────────────────┐
│  SIDEBAR (Kiri)          │  MAIN AREA (Tengah/Kanan)     │
│  ─────────────────────   │  ──────────────────────────── │
│                          │                               │
│  📊 Pilih Saham          │  [ Nama Saham — Ticker ]      │
│  ┌──────────────────┐    │                               │
│  │ Maybank ▾        │    │  ┌────────────────────────┐   │
│  └──────────────────┘    │  │                        │   │
│                          │  │   CARTA CANDLESTICK    │   │
│  📅 Tempoh Masa          │  │      (Plotly)          │   │
│  ○ 1 Bulan               │  │   [interaktif: zoom,   │   │
│  ● 3 Bulan               │  │    hover, pan]         │   │
│  ○ 6 Bulan               │  │                        │   │
│  ○ 1 Tahun               │  └────────────────────────┘   │
│                          │                               │
│  📈 Indikator            │  ┌────────────────────────┐   │
│  ☑ SMA (20, 50)          │  │   SUB-CHART: RSI       │   │
│  ☑ RSI (14)              │  └────────────────────────┘   │
│  ☑ MACD                  │                               │
│                          │  ┌────────────────────────┐   │
│  ──────────────────       │  │   SUB-CHART: MACD      │   │
│  ℹ️  Terakhir dikemas:    │  └────────────────────────┘   │
│  31 Jul 2026, 10:35       │                               │
└──────────────────────────────────────────────────────────┘
```

---

## Spesifikasi Komponen

### Sidebar

| Komponen | Jenis | Huraian |
|----------|-------|---------|
| Pemilih Saham | `st.selectbox` | Dropdown dengan nama saham dari Google Sheet |
| Tempoh Masa | `st.radio` | Pilihan: 1M, 3M, 6M, 1Y |
| Toggle SMA | `st.checkbox` | Aktif/tutup lapisan SMA pada carta |
| Toggle RSI | `st.checkbox` | Aktif/tutup sub-carta RSI |
| Toggle MACD | `st.checkbox` | Aktif/tutup sub-carta MACD |

### Carta Utama (Candlestick)

- **Jenis**: Plotly `go.Candlestick`
- **Warna Naik**: `#26A69A` (teal — lebih lembut dari hijau terang)
- **Warna Turun**: `#EF5350` (merah — jelas tapi tidak terlalu garang)
- **SMA**: Garisan nipis dengan warna berbeza (SMA20 = biru, SMA50 = oren)
- **Latar Belakang**: Putih `#FFFFFF`
- **Grid**: Abu-abu sangat muda `#F5F5F5`
- **Hover**: Tooltip menunjukkan OHLC + tarikh

### Sub-Carta RSI

- Garisan RSI berwarna ungu
- Garis panduan (dashed) pada paras **70** (overbought) dan **30** (oversold)
- Zon overbought/oversold dibayang dengan warna sangat telus

### Sub-Carta MACD

- **MACD Line**: Biru
- **Signal Line**: Oren
- **Histogram**: Hijau (positif) / Merah (negatif)

---

## Palet Warna

| Token | Hex | Kegunaan |
|-------|-----|---------|
| `--color-up` | `#26A69A` | Candlestick naik |
| `--color-down` | `#EF5350` | Candlestick turun |
| `--color-sma20` | `#2196F3` | Garisan SMA 20 |
| `--color-sma50` | `#FF9800` | Garisan SMA 50 |
| `--color-rsi` | `#9C27B0` | Garisan RSI |
| `--color-macd` | `#2196F3` | Garisan MACD |
| `--color-signal` | `#FF9800` | Garisan Signal MACD |
| `--color-bg` | `#FFFFFF` | Latar belakang |
| `--color-grid` | `#F5F5F5` | Grid carta |
| `--color-text` | `#212121` | Teks utama |
| `--color-muted` | `#9E9E9E` | Teks kecil/sub |
