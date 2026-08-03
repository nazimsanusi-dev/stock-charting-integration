"""
data/sheet_loader.py
Reads the stock list from Google Sheets using a Service Account.
Supports selecting any worksheet within the spreadsheet.
"""

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]


def _get_gspread_client() -> gspread.Client:
    """Authenticate with Google using credentials stored in Streamlit Secrets."""
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES,
    )
    return gspread.authorize(creds)


def get_spreadsheet_options() -> list[tuple[str, str]]:
    """
    Return list of (label, url) tuples for all configured spreadsheets.

    Supports two formats in secrets.toml:
      - New multi-URL:  [google_sheets] with urls = [...] and labels = [...]
      - Legacy single:  [google_sheet] with spreadsheet_url = "..."
    """
    secrets = st.secrets

    # New multi-spreadsheet format
    if "google_sheets" in secrets:
        cfg = secrets["google_sheets"]
        urls = list(cfg.get("urls", []))
        labels = list(cfg.get("labels", []))
        # Pad labels if fewer than urls
        while len(labels) < len(urls):
            labels.append(f"Spreadsheet {len(labels) + 1}")
        return [(labels[i], urls[i]) for i in range(len(urls)) if urls[i]]

    # Legacy single-spreadsheet format
    if "google_sheet" in secrets:
        cfg = secrets["google_sheet"]
        url = cfg.get("spreadsheet_url") or cfg.get("url", "")
        label = cfg.get("label", "Spreadsheet 1")
        if url:
            return [(label, url)]

    return []


def _get_sheet_url() -> str:
    """Return the first configured spreadsheet URL (legacy helper)."""
    options = get_spreadsheet_options()
    return options[0][1] if options else ""


@st.cache_data(ttl=3600)
def load_sheet_names(spreadsheet_url: str = "") -> list[str]:
    """
    Return the list of worksheet names in the given spreadsheet.
    Falls back to ['Sheet1'] on any failure.
    """
    url = spreadsheet_url or _get_sheet_url()
    try:
        client = _get_gspread_client()
        spreadsheet = client.open_by_url(url)
        return [ws.title for ws in spreadsheet.worksheets()]
    except Exception:
        return ["Sheet1"]


@st.cache_data(ttl=3600)
def load_full_sheet_df(sheet_name: str, spreadsheet_url: str = "") -> pd.DataFrame:
    """
    Loads all columns and rows from the specified worksheet tab.
    Cached to prevent hitting Google API quotas on re-renders.
    """
    url = spreadsheet_url or _get_sheet_url()
    try:
        client = _get_gspread_client()
        spreadsheet = client.open_by_url(url)
        worksheet = spreadsheet.worksheet(sheet_name)
        
        records = worksheet.get_all_records()
        if records:
            return pd.DataFrame(records)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading full sheet data from '{sheet_name}': {e}")
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def load_stock_list(sheet_name: str = "Sheet1", spreadsheet_url: str = "") -> pd.DataFrame:
    """
    Pull the stock list from the specified worksheet.

    Args:
        sheet_name: Name of the worksheet tab to read.
        spreadsheet_url: URL of the spreadsheet (uses first configured URL if omitted).

    Returns:
        DataFrame with columns Name and Symbol.
        Returns an empty DataFrame on failure.
    """
    url = spreadsheet_url or _get_sheet_url()
    try:
        # Optimization: Reuse load_full_sheet_df to benefit from cached API calls
        df = load_full_sheet_df(sheet_name, url)

        if df.empty:
            return pd.DataFrame(columns=["Name", "Symbol"])

        # Normalise column names — support Stock_Name/Ticker_Code variants
        rename: dict[str, str] = {}
        for col in df.columns:
            cl = str(col).lower().strip()
            if cl in ("name", "stock_name", "nama"):
                rename[col] = "Name"
            elif cl in ("symbol", "ticker", "ticker_code", "kod"):
                rename[col] = "Symbol"
        df = df.rename(columns=rename)

        if "Name" not in df.columns or "Symbol" not in df.columns:
            st.error("Sheet mesti ada lajur 'Name' dan 'Symbol' (atau Stock_Name / Ticker_Code).")
            return pd.DataFrame(columns=["Name", "Symbol"])

        return df[["Name", "Symbol"]].dropna()
    except Exception as e:
        st.error(f"Gagal membaca Google Sheet '{sheet_name}': {e}")
        return pd.DataFrame(columns=["Name", "Symbol"])
