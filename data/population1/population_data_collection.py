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

PR_FIPS = [
    '001','003','005','007','009','011','013','015','017','019','021','023','025','027',
    '029','031','033','035','037','039','041','043','045','047','049','051','053','054',
    '055','057','059','061','063','065','067','069','071','073','075','077','079','081',
    '083','085','087','089','091','093','095','097','099','101','103','105','107','109',
    '111','113','115','117','119','121','123','125','127','129','131','133','135','137',
    '139','141','143','145','147','149','151','153'
]

# =============================
# HELPER FUNCTIONS
# =============================
def clean_cols(df):
    df.columns = df.columns.str.strip().str.lower().str.replace("\ufeff", "", regex=False)
    return df

def detect_date_col(cols):
    for c in cols:
        if "date" in c: return c
    return cols[0]

def safe_float(val):
    try:
        f = float(val)
        return f if f >= 0 else 0.0
    except (ValueError, TypeError):
        return 0.0

def aggregate_moe(moes):
    return math.sqrt(sum([m**2 for m in moes]))

def get_edu_vars(year):
    if year < 2015 or year >= 2023:
        return "S1501_C02_006E", "S1501_C02_006M"
    else:
        return "S1501_C02_015E", "S1501_C02_015M"

def get_naics_variable_name(year):
    if year >= 2017: return "NAICS2017"
    elif year >= 2012: return "NAICS2012"
    elif year >= 2007: return "NAICS2007"
    return "NAICS2002"

# =============================
# 1. LOAD & PROCESS CPI
# =============================
print("📉 Fetching CPI data for real income adjustment...")
cpi_df = pd.read_csv(CPI_URL)
cpi_df = clean_cols(cpi_df)
date_col = detect_date_col(cpi_df.columns)
val_col = [c for c in cpi_df.columns if c != date_col][0]
cpi_df['year'] = pd.to_datetime(cpi_df[date_col]).dt.year
annual_cpi = cpi_df.groupby('year')[val_col].mean().to_dict()
latest_cpi = annual_cpi[max(annual_cpi.keys())]

# =============================
# 2. CENSUS DATA COLLECTION
# =============================
print("\n📊 Downloading Complete Master Profile (2010–2024)...")
records = []
years = range(2010, 2025) 
fips_str = ",".join(PR_FIPS)

for i, year in enumerate(years, start=1):
    sys.stdout.write(f"\rFetching {year} ({i}/{len(years)}) ...")
    sys.stdout.flush()

    edu_e, edu_m = get_edu_vars(year)
    naics_var = get_naics_variable_name(year)

    urls = {
        "pop_house": f"https://api.census.gov/data/{year}/acs/acs5?get=NAME,B01001_001E,B01001_001M,B25001_001E,B25001_001M&for=county:{fips_str}&in=state:72&key={API_KEY}",
        "labor_income": f"https://api.census.gov/data/{year}/acs/acs5/subject?get=NAME,S2301_C01_001E,S2301_C01_001M,S2301_C04_001E,S2301_C04_001M,S2301_C03_001E,S2301_C03_001M,S2301_C02_001E,S2301_C02_001M,S1901_C01_012E,S1901_C01_012M&for=county:{fips_str}&in=state:72&key={API_KEY}",
        "edu_pct": f"https://api.census.gov/data/{year}/acs/acs5/subject?get=NAME,{edu_e},{edu_m},S1501_C02_009E,S1501_C02_009M&for=county:{fips_str}&in=state:72&key={API_KEY}",
        "edu_counts": f"https://api.census.gov/data/{year}/acs/acs5?get=NAME,B15003_001E,B15003_001M,B15003_017E,B15003_017M,B15003_018E,B15003_018M,B15003_022E,B15003_022M,B15003_023E,B15003_023M,B15003_024E,B15003_024M,B15003_025E,B15003_025M&for=county:{fips_str}&in=state:72&key={API_KEY}",
        "cbp": f"https://api.census.gov/data/{year}/cbp?get=NAME,ESTAB&for=county:{fips_str}&in=state:72&{naics_var}=00&key={API_KEY}"
    }
    if year >= 2012: 
        urls["health"] = f"https://api.census.gov/data/{year}/acs/acs5/subject?get=NAME,S2701_C05_001E,S2701_C05_001M&for=county:{fips_str}&in=state:72&key={API_KEY}"

    payloads = {}
    for k, u in urls.items():
        r = requests.get(u, timeout=60)
        if r.status_code == 200:
            raw = r.json()
            h = raw[0]
            s_idx, c_idx = h.index("state"), h.index("county")
            payloads[k] = {f"{row[s_idx]}{row[c_idx]}": row for row in raw[1:]}

    curr_cpi = annual_cpi.get(year, latest_cpi)

    for fips in PR_FIPS:
        geoid = f"72{fips}"
        p_h = payloads.get("pop_house", {}).get(geoid)
        l_i = payloads.get("labor_income", {}).get(geoid)
        ep = payloads.get("edu_pct", {}).get(geoid)
        ec = payloads.get("edu_counts", {}).get(geoid)
        cbp = payloads.get("cbp", {}).get(geoid)
        h_cov = payloads.get("health", {}).get(geoid)

        if not all([p_h, l_i, ep, ec]): continue

        # Calculations
        nom_inc = safe_float(l_i[9])
        real_inc = (nom_inc * latest_cpi) / curr_cpi if curr_cpi > 0 else nom_inc
        
        # Education Counts Aggregates
        hs_count = safe_float(ec[3]) + safe_float(ec[5])
        hs_moe = aggregate_moe([safe_float(ec[4]), safe_float(ec[6])])

        records.append({
            "year": year,
            "municipio": p_h[0].replace(", Puerto Rico", ""),
            "geoid": geoid,
            # Population & Housing (Restored 16+ columns)
            "total_population": safe_float(p_h[1]),
            "total_population_moe": safe_float(p_h[2]),
            "total_population_16plus": safe_float(l_i[1]),
            "total_population_16plus_moe": safe_float(l_i[2]),
            "total_housing_units": safe_float(p_h[3]),
            "total_housing_units_moe": safe_float(p_h[4]),
            # Labor
            "unemployment_rate_pct": safe_float(l_i[3]),
            "unemployment_rate_moe": safe_float(l_i[4]),
            "labor_force_participation_pct": safe_float(l_i[7]),
            "labor_force_participation_moe": safe_float(l_i[8]),
            # Income & CPI
            "median_income_nominal": nom_inc,
            "median_income_real": round(real_inc, 2),
            "median_income_moe": safe_float(l_i[10]),
            "cpi": round(curr_cpi, 2),
            # Education
            "total_population_25plus": safe_float(ec[1]),
            "hs_graduate_pct": safe_float(ep[3]),
            "hs_graduate_count": hs_count,
            "hs_graduate_moe": hs_moe,
            "bachelors_plus_pct": safe_float(ep[1]),
            "bachelors_count": safe_float(ec[7]),
            "doctorate_count": safe_float(ec[13]),
            "doctorate_moe": safe_float(ec[14]),
            # Misc
            "establishment_count": safe_float(cbp[1]) if cbp else None,
            "uninsured_pct": safe_float(h_cov[1]) if h_cov else None,
            "uninsured_moe": safe_float(h_cov[2]) if h_cov else None
        })

# =============================
# 3. SAVE TO CSV AND JSON
# =============================
df = pd.DataFrame(records).sort_values(["year", "municipio"]).reset_index(drop=True)

csv_path = OUT / "puerto_rico_master_profile_2010_2024.csv"
json_path = OUT / "puerto_rico_master_profile_2010_2024.json"

df.to_csv(csv_path, index=False)
df.to_json(json_path, orient="records", indent=2, force_ascii=False)

print(f"\n✅ SUCCESS! All previous columns preserved and 16+ pop restored.")
print(f"   CSV: {csv_path.name}")
print(f"   JSON: {json_path.name}")
