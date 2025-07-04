import os
import requests
import pandas as pd

# URL to the latest price list Excel file from Alko's official site (Update link if data fetch fails)
URL = "https://www.alko.fi/INTERSHOP/static/WFS/Alko-OnlineShop-Site/-/Alko-OnlineShop/fi_FI/Alkon%20Hinnasto%20Tekstitiedostona/alkon-hinnasto-tekstitiedostona.xlsx"
FILENAME = "assets/alko_price_list.xlsx"    # Local path to save downloaded Excel file
BACKUP_FILENAME = "assets/alko_price_list_backup.xlsx"  # Backup file to use if fetch fails
os.makedirs("assets", exist_ok=True)     # Ensure the directory exists before saving the file

def fetch_and_process_data():
    """
    Downloads the latest Alko price list Excel file, processes it into a clean DataFrame,
    and computes an "Alcohol per Euro" value for each product.
    Falls back to a backup file if the fetch fails.
    """

    # Delete old file if it exists (ensures only newest version exists)
    try:
        if os.path.exists(FILENAME):
            os.remove(FILENAME)

        # Send a GET request to download the file
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114.0.0.0 Safari/537.36"
        }
        response = requests.get(URL, headers=headers)
        response.raise_for_status()     # Raise an error if the request failed

        # Validate that the content is an Excel file (for troubleshooting)
        content_type = response.headers.get("Content-Type", "")
        if "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" not in response.headers.get("Content-Type",
                                                                                                           ""):
            raise ValueError(f"Downloaded file is not a valid Excel file (content-type was: {content_type})")

        # Save the file locally
        with open(FILENAME, "wb") as f:
            f.write(response.content)

        read_path = FILENAME

    except Exception as e:
        # Use backup if fetch or validation fails
        if os.path.exists(BACKUP_FILENAME):
            read_path = BACKUP_FILENAME
        else:
            raise RuntimeError(f"Failed to fetch Alko data and no backup available:\n{e}")

    # Read the file using header row at index 3 (Header row)
    df = pd.read_excel(read_path, header=3, engine="openpyxl")

    # Rename columns for clarity and consistency
    df = df.rename(columns={
        "Nimi": "Tuotenimi",
        "Hinta": "Hinta",
        "Alkoholi-%": "Alkoholi%",
        "Pullokoko": "Pullokoko",
        "Tyyppi": "Tyyppi"
    })

    # Drop rows with missing essential values
    df = df[["Tuotenimi", "Hinta", "Alkoholi%", "Pullokoko", "Tyyppi"]].dropna()

    # Normalize "tyyppi" field to lowercase & strip
    df["Tyyppi"] = df["Tyyppi"].astype(str).str.strip().str.lower()

    # Remove exact duplicate rows to avoid redundancy eg. same product appearing twice
    df = df.drop_duplicates()

    # Convert "Pullokoko" string (e.g., "0.75 l") to float (liters)
    df["Pullokoko (l)"] = df["Pullokoko"].astype(str).str.replace(" l", "", regex=False)
    df["Pullokoko (l)"] = pd.to_numeric(df["Pullokoko (l)"], errors="coerce")

    # Convert other numerical fields
    df["Hinta"] = pd.to_numeric(df["Hinta"], errors="coerce")
    df["Alkoholi%"] = pd.to_numeric(df["Alkoholi%"], errors="coerce")

    # Drop rows that failed conversion to numeric types
    df = df.dropna(subset=["Hinta", "Alkoholi%", "Pullokoko (l)"])

    # Calculate the amount of pure alcohol in liters
    df["PureAlcohol_l"] = df["Alkoholi%"] / 100 * df["Pullokoko (l)"]

    # Calculate how much alcohol you get per euro spent
    df["AlcoholPerEuro"] = df["PureAlcohol_l"] / df["Hinta"]

    # Sort by alcohol-per-euro descending
    df = df.sort_values(by="AlcoholPerEuro", ascending=False)

    # Reset the index
    return df.reset_index(drop=True), (read_path == BACKUP_FILENAME)
