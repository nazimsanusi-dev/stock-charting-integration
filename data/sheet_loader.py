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


def _get_sheet_url() -> str:
    """Return the spreadsheet URL from secrets (supports both key names)."""
    sheet_cfg = st.secrets["google_sheet"]
    return sheet_cfg.get("spreadsheet_url") or sheet_cfg.get("url", "")


@st.cache_data(ttl=3600)
def load_sheet_names() -> list[str]:
    """
    Return the list of worksheet names in the configured spreadsheet.
    Falls back to ['Sheet1'] on any failure.
    """
    try:
        client = _get_gspread_client()
        spreadsheet = client.open_by_url(_get_sheet_url())
        return [ws.title for ws in spreadsheet.worksheets()]
    except Exception:
        return ["Sheet1"]


@st.cache_data(ttl=3600)
def load_stock_list(sheet_name: str = "Sheet1") -> pd.DataFrame:
    """
    Pull the stock list from the specified worksheet.

    Args:
        sheet_name: Name of the worksheet tab to read.

    Returns:
        DataFrame with columns Name and Symbol.
        Returns an empty DataFrame on failure.
    """
    try:
        client = _get_gspread_client()
        spreadsheet = client.open_by_url(_get_sheet_url())
        worksheet = spreadsheet.worksheet(sheet_name)
        records = worksheet.get_all_records()

        df = pd.DataFrame(records)
        if df.empty:
            return pd.DataFrame(columns=["Name", "Symbol"])

        # Normalise column names — support Stock_Name/Ticker_Code variants
        rename: dict[str, str] = {}
        for col in df.columns:
            cl = col.lower().strip()
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
