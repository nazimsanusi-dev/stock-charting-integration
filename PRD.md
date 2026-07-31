# PRD — Product Requirements Document

## Tujuan

Bina aplikasi web ringan untuk memantau pergerakan harga saham secara visual dan interaktif.

## Fungsi Utama

| # | Fungsi | Huraian |
|---|--------|---------|
| 1 | **Baca Senarai Saham** | Tarik senarai nama saham dan kod ticker dari Google Sheet |
| 2 | **Ambil Data Harga** | Gunakan Yahoo Finance untuk dapatkan data harga OHLCV (Open, High, Low, Close, Volume) |
| 3 | **Papar Carta Candlestick** | Visualisasikan pergerakan harga dalam bentuk carta candlestick interaktif |
| 4 | **Technical Indicators** | Kira dan papar indikator teknikal: SMA, RSI, dan MACD |

## Skop Produk

### Dalam Skop
- Paparan carta candlestick dengan data harga harian
- Pengiraan dan paparan SMA (Simple Moving Average)
- Pengiraan dan paparan RSI (Relative Strength Index)
- Pengiraan dan paparan MACD (Moving Average Convergence Divergence)
- Pilihan tempoh masa (contoh: 1 bulan, 3 bulan, 6 bulan, 1 tahun)
- Toggle untuk aktif/tutup setiap indikator

### Luar Skop
- Fungsi beli/jual saham (bukan platform trading)
- Notifikasi harga secara real-time
- Pengurusan portfolio

## Pengguna Sasaran

Pelabur runcit dan penganalisis saham yang ingin memantau carta harga dengan pantas tanpa perlu membuka platform yang kompleks.

## Kriteria Kejayaan

- Aplikasi berjaya memuatkan senarai saham dari Google Sheet
- Carta candlestick dipaparkan dengan betul berdasarkan ticker yang dipilih
- Semua tiga indikator (SMA, RSI, MACD) berfungsi dan boleh dihidupkan/dimatikan
- Masa muatan halaman tidak melebihi 3 saat (dengan caching aktif)
