"""
data/sheet_loader.py
Reads the stock list from Google Sheets using a Service Account.
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


@st.cache_data(ttl=3600)
def load_stock_list() -> pd.DataFrame:
    """
    Pull the stock list from Google Sheet.

    Returns a DataFrame with columns: Stock_Name, Ticker_Code.
    Returns an empty DataFrame on failure.
    """
    try:
        client = _get_gspread_client()
        sheet_url: str = st.secrets["google_sheet"]["spreadsheet_url"]
        worksheet_name: str = st.secrets["google_sheet"]["worksheet_name"]

        spreadsheet = client.open_by_url(sheet_url)
        worksheet = spreadsheet.worksheet(worksheet_name)
        records = worksheet.get_all_records()

        df = pd.DataFrame(records)
        # Ensure expected columns exist
        if "Stock_Name" not in df.columns or "Ticker_Code" not in df.columns:
            st.error("Google Sheet mesti ada lajur 'Stock_Name' dan 'Ticker_Code'.")
            return pd.DataFrame(columns=["Stock_Name", "Ticker_Code"])

        return df[["Stock_Name", "Ticker_Code"]].dropna()
    except Exception as e:
        st.error(f"Gagal membaca Google Sheet: {e}")
        return pd.DataFrame(columns=["Stock_Name", "Ticker_Code"])
