import json
import math
from pathlib import Path
import requests
import pandas as pd
import sys
from datetime import datetime

# =============================
# CONFIGURATION
# =============================
API_KEY = "29dc42832697b740f9eff8ae8d61b9e544478c2b" 
OUT = Path(__file__).resolve().parent
CPI_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=CPIAUCSL"

PR_FIPS = ['001','003','005','007','009','011','013','015','017','019','021','023','025','027',
           '029','031','033','035','037','039','041','043','045','047','049','051','053','054',
           '055','057','059','061','063','065','067','069','071','073','075','077','079','081',
           '083','085','087','089','091','093','095','097','099','101','103','105','107','109',
           '111','113','115','117','119','121','123','125','127','129','131','133','135','137',
           '139','141','143','145','147','149','151','153']

# =============================
# HELPER FUNCTIONS
# =============================
def safe_float(val):
    try:
        f = float(val)
        return f if f >= 0 else 0.0
    except: return 0.0

def aggregate_moe(moes):
    return math.sqrt(sum([m**2 for m in moes]))

def get_edu_vars(year):
    if year < 2015 or year >= 2023: return "S1501_C02_006E", "S1501_C02_006M"
    return "S1501_C02_015E", "S1501_C02_015M"

def fetch_census_map(url):
    r = requests.get(url, timeout=60)
    if r.status_code != 200: return {}
    data = r.json()
    header = data[0]
    c_idx = header.index('county')
    return {f"72{row[c_idx]}": {k: row[i] for i, k in enumerate(header)} for row in data[1:]}

# =============================
# 1. ROBUST CPI LOAD (Fixes KeyError)
# =============================
print("📉 Loading CPI for Real Income Adjustment...")
cpi_df = pd.read_csv(CPI_URL)
# Normalize headers: remove BOM, strip spaces, uppercase
cpi_df.columns = cpi_df.columns.str.replace('\ufeff', '', regex=False).str.strip().str.upper()
date_col = [c for c in cpi_df.columns if 'DATE' in c][0]
val_col = [c for c in cpi_df.columns if c != date_col][0]

cpi_df['year'] = pd.to_datetime(cpi_df[date_col]).dt.year
annual_cpi = cpi_df.groupby('year')[val_col].mean().to_dict()
latest_cpi = annual_cpi[max(annual_cpi.keys())]

# =============================
# 2. MASTER COLLECTION LOOP
# =============================
records = []
years = range(2012, 2025) 
fips_str = ",".join(PR_FIPS)

print(f"\n📊 Constructing Master Profile (2012–2024)...")

for year in years:
    sys.stdout.write(f"\rProcessing {year}...")
    sys.stdout.flush()

    edu_e, edu_m = get_edu_vars(year)
    
    # URL 1: Pop, Housing, Households (Base Tables)
    u1 = f"https://api.census.gov/data/{year}/acs/acs5?get=NAME,B01001_001E,B01001_001M,B25001_001E,B25001_001M,B11005_001E,B11005_006E,B11005_010E,B26001_001E&for=county:{fips_str}&in=state:72&key={API_KEY}"
    # URL 2: Labor & Income (S2301 & S1901)
    u2 = f"https://api.census.gov/data/{year}/acs/acs5/subject?get=NAME,S2301_C01_001E,S2301_C01_001M,S2301_C04_001E,S2301_C04_001M,S2301_C02_001E,S1901_C01_012E,S1901_C01_012M&for=county:{fips_str}&in=state:72&key={API_KEY}"
    # URL 3: Poverty, Edu, Disability, Language (Stable Subject Tables)
    u3 = f"https://api.census.gov/data/{year}/acs/acs5/subject?get=NAME,S1701_C03_001E,S1501_C02_002E,{edu_e},{edu_m},S1810_C03_001E,S1601_C02_003E&for=county:{fips_str}&in=state:72&key={API_KEY}"
    # URL 4: SVI Housing & Profile Metrics (DP Tables)
    u4 = f"https://api.census.gov/data/{year}/acs/acs5/profile?get=NAME,DP05_0024PE,DP05_0019PE,DP04_0012PE,DP04_0013PE,DP04_0014PE,DP04_0078PE,DP04_0058PE&for=county:{fips_str}&in=state:72&key={API_KEY}"

    d1, d2, d3, d4 = fetch_census_map(u1), fetch_census_map(u2), fetch_census_map(u3), fetch_census_map(u4)
    curr_cpi = annual_cpi.get(year, latest_cpi)

    for fips in PR_FIPS:
        geoid = f"72{fips}"
        r1, r2, r3, r4 = d1.get(geoid), d2.get(geoid), d3.get(geoid), d4.get(geoid)
        if not all([r1, r2, r3, r4]): continue

        # Logic Calcs
        nom_inc = safe_float(r2['S1901_C01_012E'])
        real_inc = (nom_inc * latest_cpi) / curr_cpi if curr_cpi > 0 else nom_inc
        total_hh = safe_float(r1['B11005_001E'])
        single_p = (safe_float(r1['B11005_006E']) + safe_float(r1['B11005_010E']))
        
        records.append({
            "year": year, "municipio": r1['NAME'].replace(", Puerto Rico", ""), "geoid": geoid,
            # Demographics (Restored 16+)
            "total_population": safe_float(r1['B01001_001E']), "total_population_moe": safe_float(r1['B01001_001M']),
            "total_population_16plus": safe_float(r2['S2301_C01_001E']), "total_population_16plus_moe": safe_float(r2['S2301_C01_001M']),
            # Labor & Economy
            "unemployment_rate_pct": safe_float(r2['S2301_C04_001E']), "labor_force_participation_pct": safe_float(r2['S2301_C02_001E']),
            "median_income_nominal": nom_inc, "median_income_real": round(real_inc, 2), "cpi": round(curr_cpi, 2),
            # Housing & Health
            "total_housing_units": safe_float(r1['B25001_001E']), "pct_no_vehicle": safe_float(r4['DP04_0058PE']),
            # SVI Theme 1: Socioeconomic
            "pct_below_poverty": safe_float(r3['S1701_C03_001E']), "pct_no_hs_diploma": safe_float(r3['S1501_C02_002E']),
            # SVI Theme 2: Household & Disability (Restored)
            "pct_aged_65_plus": safe_float(r4['DP05_0024PE']), "pct_aged_17_under": safe_float(r4['DP05_0019PE']),
            "pct_disability": safe_float(r3['S1810_C03_001E']),
            "pct_single_parent": round((single_p / total_hh * 100), 2) if total_hh > 0 else 0.0,
            # SVI Theme 3: Language
            "pct_lim_english": safe_float(r3['S1601_C02_003E']),
            # SVI Theme 4: Housing Type
            "pct_multi_unit": safe_float(r4['DP04_0012PE']) + safe_float(r4['DP04_0013PE']),
            "pct_mobile_homes": safe_float(r4['DP04_0014PE']), "pct_crowding": safe_float(r4['DP04_0078PE']),
            "pct_group_quarters": round((safe_float(r1['B26001_001E']) / safe_float(r1['B01001_001E']) * 100), 2) if safe_float(r1['B01001_001E']) > 0 else 0.0
        })

df = pd.DataFrame(records).sort_values(["year", "municipio"]).reset_index(drop=True)
filename = "puerto_rico_master_profile_2010_2024"
df.to_csv(OUT / f"{filename}.csv", index=False)
df.to_json(OUT / f"{filename}.json", orient="records", indent=2, force_ascii=False)
print(f"\n✅ RECONSTRUCTION COMPLETE. {filename}.csv generated with all restored columns.")
