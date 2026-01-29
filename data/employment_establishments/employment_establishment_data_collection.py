#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
establishment_data_collection.py — Modified to collect Establishments
(Output structure matches municipios_acs_s1901_median_income_2010_2023_wide.json)
"""

import json
import requests
import pandas as pd
from pathlib import Path
from datetime import date, datetime
import sys
import os # Added for environment variable access

# API Key is sensitive. It's best practice to load it from an environment variable.
# For simplicity and direct use in this script, I'll keep the placeholder but recommend E-VAR.
API_KEY = os.environ.get("CENSUS_API_KEY", "29dc42832697b740f9eff8ae8d61b9e544478c2b")
OUT = Path(__file__).resolve().parent
START_YEAR = 2010

def safe_int(val):
    """Safely converts string value to int, handling 'N' and '0' as 0."""
    try:
        if val in ('N', '0'):
            return 0
        return int(val)
    except Exception:
        return None

def get_naics_variable_name(year):
    """Returns the correct NAICS variable name for the CBP API by year."""
    if year >= 2017: return "NAICS2017"
    elif year >= 2012: return "NAICS2012"
    elif year >= 2007: return "NAICS2007"
    return "NAICS2002"

# --------------------------------------------------------
# 1. Determine available CBP years
# --------------------------------------------------------
# Set the current year to the maximum available CBP data, or the current year
# We'll assume the latest year for which data is available is current_year - 2
current_year = date.today().year
latest_data_year = current_year - 2 
years = [y for y in range(START_YEAR, latest_data_year + 1)]

if len(years) < 2:
    raise RuntimeError("❌ Not enough valid CBP years found.")

# --------------------------------------------------------
# 2. Download data (Establishment Count)
# --------------------------------------------------------
print("📊 Downloading Total Employer Establishments from CBP...")
# VARS now requests the Number of Establishments (ESTAB)
VARS = ["NAME", "ESTAB"] 
records, successful_years = [], []

for i, year in enumerate(years, start=1):
    naics_var = get_naics_variable_name(year)
    url = (
        f"https://api.census.gov/data/{year}/cbp"
        f"?get={','.join(VARS)}&for=county:*&in=state:72&{naics_var}=00&key={API_KEY}"
    )
    sys.stdout.write(f"\rFetching {year} ({i}/{len(years)})...")
    sys.stdout.flush()
    try:
        r = requests.get(url, timeout=60)
        if r.status_code != 200:
            print(f"\n⚠️ Error {r.status_code} for {year}")
            continue
        data = r.json()
        header, *rows = data
        idx = {k: i for i, k in enumerate(header)}
        if not rows: continue
        successful_years.append(year)
        for row in rows:
            municipio = row[idx["NAME"]].replace(" Municipio, Puerto Rico", "")
            if municipio == "Puerto Rico":
                continue
            records.append({
                "year": year,
                "Municipio": municipio,
                "Establishments": safe_int(row[idx["ESTAB"]]) # Changed to ESTAB
            })
    except Exception as e:
        print(f"\n❌ {year} failed: {e}")
        continue

if len(successful_years) < 2:
    print("🛑 Need at least two valid years.")
    sys.exit(0)

# --------------------------------------------------------
# 3. Build dataframe
# --------------------------------------------------------
df = pd.DataFrame(records)
df = df.sort_values(["Municipio", "year"]).dropna(subset=["Establishments"])

# Add islandwide total
island = (
    df.groupby("year", as_index=False)["Establishments"]
    .sum()
    .assign(Municipio="Puerto Rico")
)
df = pd.concat([df, island], ignore_index=True)

# --------------------------------------------------------
# 4. Pivot to wide format (CRITICAL for structural parity)
# --------------------------------------------------------
# Pivot using 'Establishments' column
pivot = df.pivot(index="Municipio", columns="year", values="Establishments").reset_index()
pivot.columns.name = None

# Rename the Establishment Count columns to the year string to match the income JSON structure
# This is the key change for compatibility: Nominal income uses '2023', so establishment count uses '2023'
pivot = pivot.rename(columns={y: str(y) for y in successful_years})

first, prev, last = successful_years[0], successful_years[-2], successful_years[-1]
first_str, prev_str, last_str = str(first), str(prev), str(last)

# Calculate change metrics, referencing the columns by their string year name
pivot[f"Change_{prev_str}_{last_str}"] = pivot[last_str] - pivot[prev_str]
pivot[f"Pct_Change_{prev_str}_{last_str}"] = (pivot[f"Change_{prev_str}_{last_str}"] / pivot[prev_str]) * 100
pivot[f"Cum_Change_{first_str}_{last_str}"] = pivot[last_str] - pivot[first_str]
pivot[f"Cum_Pct_Change_{first_str}_{last_str}"] = (pivot[f"Cum_Change_{first_str}_{last_str}"] / pivot[first_str]) * 100

# Add RealIncome_* and Real_* fields as None to ensure structural parity
# These fields are meaningless for establishment count but required for HTML compatibility
for y in successful_years:
    pivot[f"RealIncome_{y}"] = None

for key in [
    f"Real_Change_{prev_str}_{last_str}",
    f"Real_Pct_Change_{prev_str}_{last_str}",
    f"Real_Cum_Change_{first_str}_{last_str}",
    f"Real_Cum_Pct_Change_{first_str}_{last_str}",
]:
    pivot[key] = None

# --------------------------------------------------------
# 5. Add metadata and save JSON
# --------------------------------------------------------
records = pivot.to_dict(orient="records")

metadata = {
    "metadata": {
        "source": "U.S. Census Bureau, County Business Patterns (CBP), NAICS 00 (All Industries)",
        "units": "Number of Employer Establishments (as of March 12)",
        "islandwide_aggregation": True,
        "data_years": [str(y) for y in successful_years],
        "updated": datetime.now().strftime("%Y-%m-%d"),
        "notes": (
            "Establishment counts use year keys (e.g., '2023') to maintain structural parity "
            "with the income JSON. RealIncome_* and Real_* fields are null placeholders."
        )
    }
}

records.append(metadata)

# Use a new filename that indicates the data content
json_path = OUT / f"municipios_cbp_establishments_{START_YEAR}_{last_str}_wide.json"
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(records, f, indent=2, ensure_ascii=False)

print(f"\n✅ Saved JSON → {json_path.name}")
print("🎉 Structural parity with income JSON achieved.")
