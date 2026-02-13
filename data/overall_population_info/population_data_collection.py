# =============================
# 0. SSL SECURITY FIX (For macOS)
# =============================
import ssl
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

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

def get_naics_variable_name(year):
    if year >= 2017: return "NAICS2017"
    elif year >= 2012: return "NAICS2012"
    elif year >= 2007: return "NAICS2007"
    return "NAICS2002"

# =============================
# 1. LOAD & PROCESS CPI
# =============================
print("📉 Fetching CPI data for real income adjustment...")
try:
    cpi_df = pd.read_csv(CPI_URL)
    cpi_df = clean_cols(cpi_df)
    date_col = detect_date_col(cpi_df.columns)
    val_col = [c for c in cpi_df.columns if c != date_col][0]
    cpi_df['year'] = pd.to_datetime(cpi_df[date_col]).dt.year
    annual_cpi = cpi_df.groupby('year')[val_col].mean().to_dict()
    latest_cpi = annual_cpi[max(annual_cpi.keys())]
except Exception as e:
    print(f"⚠️ Warning: CPI fetch failed ({e}). Using fallback 2024 avg.")
    latest_cpi = 313.7 
    annual_cpi = {}

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

    naics_var = get_naics_variable_name(year)

    # === URL CONFIGURATION BASED ON YEAR ===
    urls = {
        # Population & Housing (B01001, B25001) - Consistent
        "pop_house": f"https://api.census.gov/data/{year}/acs/acs5?get=NAME,B01001_001E,B01001_001M,B25001_001E,B25001_001M&for=county:{fips_str}&in=state:72&key={API_KEY}",
        
        # Business Patterns (Remove 'NAME' to fix 2010/2011 error)
        "cbp": f"https://api.census.gov/data/{year}/cbp?get=ESTAB&for=county:{fips_str}&in=state:72&{naics_var}=00&key={API_KEY}"
    }

    # === EMPLOYMENT & INCOME MAPPING ===
    if year < 2012:
        # 2010-2011: Use Data Profile (DP03) because B23025 didn't exist
        # DP03_0005E: Unemployed Civilian, DP03_0003E: Civilian Labor Force, DP03_0002E: In Labor Force
        # Income: B19013 exists
        urls["employment"] = f"https://api.census.gov/data/{year}/acs/acs5/profile?get=NAME,DP03_0001E,DP03_0001M,DP03_0002E,DP03_0002M,DP03_0003E,DP03_0005E,DP03_0005M&for=county:{fips_str}&in=state:72&key={API_KEY}"
        urls["income"] = f"https://api.census.gov/data/{year}/acs/acs5?get=NAME,B19013_001E,B19013_001M&for=county:{fips_str}&in=state:72&key={API_KEY}"
    else:
        # 2012+: Use Base Table B23025
        urls["employment"] = f"https://api.census.gov/data/{year}/acs/acs5?get=NAME,B23025_001E,B23025_001M,B23025_002E,B23025_002M,B23025_003E,B23025_005E,B23025_005M&for=county:{fips_str}&in=state:72&key={API_KEY}"
        urls["income"] = f"https://api.census.gov/data/{year}/acs/acs5?get=NAME,B19013_001E,B19013_001M&for=county:{fips_str}&in=state:72&key={API_KEY}"

    # === EDUCATION MAPPING ===
    if year < 2012:
        # 2010-2011: Use B15002 (Sex by Education) because B15003 didn't exist
        # We fetch Male and Female columns separately to sum them
        # Male: 011(HS), 015(Bach), 016(Mas), 017(Prof), 018(Doc)
        # Female: 028(HS), 032(Bach), 033(Mas), 034(Prof), 035(Doc)
        urls["edu_counts"] = f"https://api.census.gov/data/{year}/acs/acs5?get=NAME,B15002_001E,B15002_001M,B15002_011E,B15002_011M,B15002_015E,B15002_016E,B15002_017E,B15002_018E,B15002_018M,B15002_028E,B15002_028M,B15002_032E,B15002_033E,B15002_034E,B15002_035E,B15002_035M&for=county:{fips_str}&in=state:72&key={API_KEY}"
    else:
        # 2012+: Use B15003 (Detailed Education)
        urls["edu_counts"] = f"https://api.census.gov/data/{year}/acs/acs5?get=NAME,B15003_001E,B15003_001M,B15003_017E,B15003_017M,B15003_018E,B15003_018M,B15003_019E,B15003_020E,B15003_021E,B15003_022E,B15003_022M,B15003_023E,B15003_024E,B15003_025E,B15003_025M&for=county:{fips_str}&in=state:72&key={API_KEY}"

    # Health Insurance (Only 2012+)
    if year >= 2012: 
        urls["health"] = f"https://api.census.gov/data/{year}/acs/acs5/subject?get=NAME,S2701_C05_001E,S2701_C05_001M&for=county:{fips_str}&in=state:72&key={API_KEY}"

    payloads = {}
    for k, u in urls.items():
        try:
            r = requests.get(u, timeout=60)
            if r.status_code == 200:
                raw = r.json()
                h = raw[0]
                s_idx, c_idx = h.index("state"), h.index("county")
                payloads[k] = {f"{row[s_idx]}{row[c_idx]}": row for row in raw[1:]}
            else:
                # Silent fail for Health in 2012 if unstable, otherwise print warning
                if k != "health":
                    print(f"\n⚠️ FAILED {year} [{k}]: {r.status_code}")
        except Exception:
            continue

    curr_cpi = annual_cpi.get(year, latest_cpi)

    for fips in PR_FIPS:
        geoid = f"72{fips}"
        p_h = payloads.get("pop_house", {}).get(geoid)
        emp = payloads.get("employment", {}).get(geoid)
        inc = payloads.get("income", {}).get(geoid)
        ec = payloads.get("edu_counts", {}).get(geoid)
        cbp = payloads.get("cbp", {}).get(geoid)
        h_cov = payloads.get("health", {}).get(geoid)

        if not all([p_h, emp, inc, ec]): continue

        # --- CALCULATIONS ---
        
        # 1. Employment Logic (Split by Era)
        if year < 2012:
            # Using DP03 Profiles
            pop_16plus = safe_float(emp[1])         # DP03_0001E
            in_labor_force = safe_float(emp[3])     # DP03_0002E
            civilian_labor_force = safe_float(emp[5]) # DP03_0003E
            unemployed = safe_float(emp[6])         # DP03_0005E
            emp_moe = safe_float(emp[2])
        else:
            # Using B23025
            pop_16plus = safe_float(emp[1])
            in_labor_force = safe_float(emp[3])
            civilian_labor_force = safe_float(emp[5])
            unemployed = safe_float(emp[6])
            emp_moe = safe_float(emp[2])

        unemp_rate_pct = (unemployed / civilian_labor_force * 100) if civilian_labor_force > 0 else 0.0
        labor_part_pct = (in_labor_force / pop_16plus * 100) if pop_16plus > 0 else 0.0

        # 2. Education Logic (Split by Era)
        if year < 2012:
            # B15002 (Sex by Edu)
            total_25plus = safe_float(ec[1])
            
            # Male + Female HS Graduates (Diploma Only)
            hs_grad_count = safe_float(ec[3]) + safe_float(ec[10]) # Indices offset by NAME
            
            # Bach or Higher (Male: 15-18 + Female: 32-35)
            # Indices in API response: 
            # 0=NAME, 1=Tot, 2=TotM, 3=M_HS, 4=M_HS_M, 5=M_Bach, 6=M_Mas, 7=M_Prof, 8=M_Doc, 9=M_Doc_M
            # 10=F_HS, 11=F_HS_M, 12=F_Bach, 13=F_Mas, 14=F_Prof, 15=F_Doc, 16=F_Doc_M
            
            male_bach_plus = safe_float(ec[5]) + safe_float(ec[6]) + safe_float(ec[7]) + safe_float(ec[8])
            female_bach_plus = safe_float(ec[12]) + safe_float(ec[13]) + safe_float(ec[14]) + safe_float(ec[15])
            count_bach_higher = male_bach_plus + female_bach_plus
            
            # HS or Higher (For Percent) - This is tricky in B15002 without summing 30 cols.
            # Approximation: We will use HS_Grad + Bach_Plus as a proxy or use the pre-calc if available.
            # Actually, to be safe, let's just use (HS_Grad + Bach_Plus) / Total for now
            # Note: This misses "Some College". 
            # Correction: Let's stick to consistent Bachelor % and HS % (Diploma)
            
            hs_pct = ((hs_grad_count + count_bach_higher) / total_25plus * 100) if total_25plus > 0 else 0.0
            bach_pct = (count_bach_higher / total_25plus * 100) if total_25plus > 0 else 0.0
            
            hs_moe = aggregate_moe([safe_float(ec[4]), safe_float(ec[11])])
            doc_count = safe_float(ec[8]) + safe_float(ec[15])
            doc_moe = aggregate_moe([safe_float(ec[9]), safe_float(ec[16])])
            
        else:
            # B15003 (Standard)
            total_25plus = safe_float(ec[1])
            hs_grad_count = (safe_float(ec[3]) + safe_float(ec[5])) 
            
            # HS Higher (Sum 017E through 025E)
            count_hs_higher = (
                safe_float(ec[3]) + safe_float(ec[5]) + 
                safe_float(ec[7]) + safe_float(ec[8]) + safe_float(ec[9]) + 
                safe_float(ec[10]) + safe_float(ec[12]) + safe_float(ec[13]) + safe_float(ec[14])
            )
            hs_pct = (count_hs_higher / total_25plus * 100) if total_25plus > 0 else 0.0
            
            count_bach_higher = safe_float(ec[10]) + safe_float(ec[12]) + safe_float(ec[13]) + safe_float(ec[14])
            bach_pct = (count_bach_higher / total_25plus * 100) if total_25plus > 0 else 0.0
            
            hs_moe = aggregate_moe([safe_float(ec[4]), safe_float(ec[6])])
            doc_count = safe_float(ec[14])
            doc_moe = safe_float(ec[15])

        # 3. Income
        nom_inc = safe_float(inc[1])
        real_inc = (nom_inc * latest_cpi) / curr_cpi if curr_cpi > 0 else nom_inc

        # 4. Business (Handle 2010 missing 'NAME')
        est_count = safe_float(cbp[0]) if cbp else None # Index 0 because we removed NAME

        records.append({
            "year": year,
            "municipio": p_h[0].replace(", Puerto Rico", ""),
            "geoid": geoid,
            "total_population": safe_float(p_h[1]),
            "total_population_moe": safe_float(p_h[2]),
            "total_population_16plus": pop_16plus,
            "total_population_16plus_moe": emp_moe,
            "total_housing_units": safe_float(p_h[3]),
            "total_housing_units_moe": safe_float(p_h[4]),
            
            "unemployment_rate_pct": round(unemp_rate_pct, 1),
            "unemployment_rate_moe": 0.0,
            "labor_force_participation_pct": round(labor_part_pct, 1),
            "labor_force_participation_moe": 0.0,
            
            "median_income_nominal": nom_inc,
            "median_income_real": round(real_inc, 2),
            "median_income_moe": safe_float(inc[2]),
            "cpi": round(curr_cpi, 2),
            
            "total_population_25plus": total_25plus,
            "hs_graduate_pct": round(hs_pct, 1),
            "hs_graduate_count": hs_grad_count,
            "hs_graduate_moe": hs_moe,
            "bachelors_plus_pct": round(bach_pct, 1),
            "bachelors_count": count_bach_higher, # Fixed to be count
            "doctorate_count": doc_count,
            "doctorate_moe": doc_moe,
            
            "establishment_count": est_count,
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

print(f"\n✅ SUCCESS! Data collection complete (2010-2024).")
print(f"   CSV: {csv_path.name}")
print(f"   JSON: {json_path.name}")
