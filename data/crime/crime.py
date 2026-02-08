#!/usr/bin/env python3
"""
Puerto Rico Crime Data Collector - The "Link Finder" Edition
Strategy:
1. Visit the main FBI "Crime in the US" page for each year.
2. Search ALL links on that page for "Puerto Rico" + ".xls".
3. Download the first match found.
"""

import os
import io
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup

# ==========================================
# CONFIGURATION
# ==========================================
OUT_DIR = "data/crime_pr"
START_YEAR = 2010
END_YEAR = 2019

# The FBI site structure is generally: 
# https://ucr.fbi.gov/crime-in-the-u.s/{year}/crime-in-the-u.s.-{year}
# But we will search recursively if needed.
BASE_UCR_URL = "https://ucr.fbi.gov/crime-in-the-u.s/{year}/crime-in-the-u.s.-{year}"

# Fallback: specific known weird URLs for tricky years
MANUAL_OVERRIDES = {
    2019: "https://ucr.fbi.gov/crime-in-the-u.s/2019/crime-in-the-u.s.-2019/tables/table-11/table-11-state-cuts/puerto-rico.xls",
    2018: "https://ucr.fbi.gov/crime-in-the-u.s/2018/crime-in-the-u.s.-2018/tables/table-11/table-11-state-cuts/puerto-rico.xls",
    2017: "https://ucr.fbi.gov/crime-in-the-u.s/2017/crime-in-the-u.s.-2017/tables/table-11/table-11-state-cuts/puerto-rico.xls",
}

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def fetch_html(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            return r.text
    except Exception as e:
        print(f"    [!] Error fetching {url}: {e}")
    return None

def find_pr_link_on_page(year, html, base_url):
    """
    Scans HTML for any <a> tag that:
    1. Contains text "Puerto Rico" OR href contains "puerto-rico"
    2. Ends in .xls or .xlsx
    """
    soup = BeautifulSoup(html, "html.parser")
    
    # 1. Direct Search
    for a in soup.find_all("a", href=True):
        href = a["href"].lower()
        text = a.get_text().lower()
        
        if ("puerto" in href or "puerto" in text) and ("xls" in href):
            # Resolve relative links
            if not href.startswith("http"):
                # Handle relative URLs carefully
                if href.startswith("/"):
                    return f"https://ucr.fbi.gov{href}" 
                else:
                    return f"{base_url}/{href}".replace("/crime-in-the-u.s.-{year}/crime-in-the-u.s.-{year}", f"/crime-in-the-u.s.-{year}")
            return a["href"]
            
    return None

def download_excel(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    print(f"    Downloading: {url} ...")
    try:
        r = requests.get(url, headers=headers, timeout=30)
        if r.status_code == 200:
            return r.content
    except Exception as e:
        print(f"    [!] Download failed: {e}")
    return None

def standardize_columns(df, year):
    """
    Standardizes disparate headers into a common format.
    Target: [year, municipio, delito, count]
    """
    # Clean column names
    df.columns = [str(c).strip().replace('\n', ' ') for c in df.columns]
    
    # 1. Identify Municipality Column
    # FBI often uses "Agency", "City", "Puerto Rico" (header row)
    mun_col = None
    for c in df.columns:
        if "Agency" in c or "City" in c or "Municipio" in c:
            mun_col = c
            break
            
    if not mun_col:
        # Fallback: First object column
        obj_cols = df.select_dtypes(include=["object"]).columns
        if len(obj_cols) > 0: mun_col = obj_cols[0]
        else: return pd.DataFrame()

    df = df.rename(columns={mun_col: "municipio"})
    
    # Filter junk rows
    df = df[df['municipio'].notna()]
    df = df[~df['municipio'].astype(str).str.contains("Note|Total|Population", case=False, na=False)]

    # 2. Identify Crime Columns (Numeric)
    # We map FBI headers to our standard "Delito" names
    numeric_cols = []
    for c in df.columns:
        if c == "municipio": continue
        
        # Verify it's a crime column (has numbers)
        try:
            # Force numeric, turning "null" or "-" into NaN
            df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
            if df[c].sum() >= 0:
                numeric_cols.append(c)
        except:
            continue

    if not numeric_cols:
        return pd.DataFrame()

    # 3. Melt
    long_df = df.melt(id_vars=["municipio"], value_vars=numeric_cols, 
                      var_name="delito", value_name="count")
    
    long_df["year"] = year
    long_df = long_df[long_df["count"] > 0] # Remove zeros
    
    # Clean up Municipality Names
    # Remove numbers (footnotes) like "San Juan2"
    long_df["municipio"] = long_df["municipio"].astype(str).str.replace(r'\d+', '', regex=True).str.strip().str.title()
    
    return long_df

def main():
    ensure_dir(OUT_DIR)
    print(f"🕵️‍♂️ Searching FBI UCR Archives for Puerto Rico ({START_YEAR}-{END_YEAR})...\n")
    
    all_data = []
    
    for year in range(START_YEAR, END_YEAR + 1):
        print(f"Processing {year}...")
        
        target_url = None
        
        # 1. Check Override First
        if year in MANUAL_OVERRIDES:
            target_url = MANUAL_OVERRIDES[year]
        else:
            # 2. Search Main Page
            base_url = BASE_UCR_URL.format(year=year)
            html = fetch_html(base_url)
            if html:
                # Try finding "Puerto Rico" link directly
                target_url = find_pr_link_on_page(year, html, base_url)
                
                # 3. If not found, try "Table 8" sub-page (Common for older years)
                if not target_url:
                    # Construct Table 8 URL guess
                    t8_url = f"{base_url}/tables/table-8/table-8-state-cuts/puerto-rico.xls"
                    # Just try downloading it blindly
                    target_url = t8_url

        if target_url:
            content = download_excel(target_url)
            if content:
                try:
                    # FBI Excel files often have header garbage in first 3-5 rows
                    # We try reading with header=3 first (standard), then header=4
                    try:
                        df = pd.read_excel(io.BytesIO(content), header=3)
                        # Check if "Murder" is in columns to verify we got the header
                        if not any("urder" in str(c) for c in df.columns):
                            raise ValueError("Header mismatch")
                    except:
                         df = pd.read_excel(io.BytesIO(content), header=4)
                    
                    std_df = standardize_columns(df, year)
                    if not std_df.empty:
                        all_data.append(std_df)
                        print(f"    ✅ Success! Extracted {len(std_df)} records.")
                    else:
                        print("    ⚠️  Parsed file but found no valid data rows.")
                except Exception as e:
                    print(f"    ❌ Failed to parse Excel: {e}")
            else:
                print("    ❌ Link found but download failed (404).")
        else:
            print("    ❌ Could not find a Puerto Rico Excel link for this year.")

    # Save
    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        # Rename common FBI weird columns to Spanish if desired, or keep English
        out_path = os.path.join(OUT_DIR, "pr_crime_fbi_2010_2019.csv")
        final_df.to_csv(out_path, index=False)
        print(f"\n🎉 COMPLETED. Saved {len(final_df)} records to {out_path}")
    else:
        print("\n❌ No data collected.")

if __name__ == "__main__":
    main()
