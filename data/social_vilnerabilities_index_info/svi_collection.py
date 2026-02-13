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

# =============================
# CONFIGURATION
# =============================
API_KEY = "29dc42832697b740f9eff8ae8d61b9e544478c2b" 
OUT = Path(__file__).resolve().parent

PR_FIPS = [
    '001','003','005','007','009','011','013','015','017','019','021','023','025','027',
    '029','031','033','035','037','039','041','043','045','047','049','051','053','054',
    '055','057','059','061','063','065','067','069','071','073','075','077','079','081',
    '083','085','087','089','091','093','095','097','099','101','103','105','107','109',
    '111','113','115','117','119','121','123','125','127','129','131','133','135','137',
    '139','141','143','145','147','149','151','153'
]

def safe_float(val):
    try:
        f = float(val)
        return f if f >= 0 else 0.0
    except (ValueError, TypeError):
        return 0.0

# =============================
# 1. DATA COLLECTION LOOP
# =============================
print("\n📊 Collecting Comprehensive SVI metrics (2010–2024)...")
records = []
years = range(2010, 2025) 
fips_str = ",".join(PR_FIPS)

for year in years:
    sys.stdout.write(f"\rProcessing Year: {year} ...")
    sys.stdout.flush()

    urls = {}
    
    # --- 1. BASIC SOCIO-ECONOMIC ---
    urls["poverty"] = f"https://api.census.gov/data/{year}/acs/acs5?get=NAME,B17001_001E,B17001_002E&for=county:{fips_str}&in=state:72&key={API_KEY}"
    urls["income"] = f"https://api.census.gov/data/{year}/acs/acs5?get=NAME,B19301_001E&for=county:{fips_str}&in=state:72&key={API_KEY}"

    # --- 2. DEMOGRAPHICS ---
    age_cols = "B01001_003E,B01001_004E,B01001_005E,B01001_006E,B01001_027E,B01001_028E,B01001_029E,B01001_030E" # <18
    age_cols_65 = "B01001_020E,B01001_021E,B01001_022E,B01001_023E,B01001_024E,B01001_025E,B01001_044E,B01001_045E,B01001_046E,B01001_047E,B01001_048E,B01001_049E" # 65+
    urls["demographics"] = f"https://api.census.gov/data/{year}/acs/acs5?get=NAME,B01001_001E,B03002_001E,B03002_003E,{age_cols},{age_cols_65}&for=county:{fips_str}&in=state:72&key={API_KEY}"

    # --- 3. SINGLE PARENT ---
    urls["single_parent"] = f"https://api.census.gov/data/{year}/acs/acs5?get=NAME,B11003_010E,B11003_016E,B11001_001E&for=county:{fips_str}&in=state:72&key={API_KEY}"

    # --- 4. EDUCATION ---
    if year < 2012:
        # B15002: Male < HS (003-010), Female < HS (020-027)
        edu_cols = "B15002_003E,B15002_004E,B15002_005E,B15002_006E,B15002_007E,B15002_008E,B15002_009E,B15002_010E"
        edu_cols_f = "B15002_020E,B15002_021E,B15002_022E,B15002_023E,B15002_024E,B15002_025E,B15002_026E,B15002_027E"
        urls["education"] = f"https://api.census.gov/data/{year}/acs/acs5?get=NAME,B15002_001E,{edu_cols},{edu_cols_f}&for=county:{fips_str}&in=state:72&key={API_KEY}"
    else:
        # B15003: Less than HS (002-016)
        edu_cols = ",".join([f"B15003_{i:03d}E" for i in range(2, 17)])
        urls["education"] = f"https://api.census.gov/data/{year}/acs/acs5?get=NAME,B15003_001E,{edu_cols}&for=county:{fips_str}&in=state:72&key={API_KEY}"

    # --- 5. EMPLOYMENT ---
    if year < 2012:
        urls["employment"] = f"https://api.census.gov/data/{year}/acs/acs5/profile?get=NAME,DP03_0005E,DP03_0003E&for=county:{fips_str}&in=state:72&key={API_KEY}"
    else:
        urls["employment"] = f"https://api.census.gov/data/{year}/acs/acs5?get=NAME,B23025_005E,B23025_003E&for=county:{fips_str}&in=state:72&key={API_KEY}"

    # --- 6. DISABILITY (FINAL FIX) ---
    if year < 2012:
        # B18101: 6 Male + 6 Female columns = 12 columns to sum
        # Male: <5(004), 5-17(007), 18-34(010), 35-64(013), 65-74(016), 75+(019)
        dis_m = "B18101_004E,B18101_007E,B18101_010E,B18101_013E,B18101_016E,B18101_019E"
        # Female: <5(023), 5-17(026), 18-34(029), 35-64(032), 65-74(035), 75+(038)
        dis_f = "B18101_023E,B18101_026E,B18101_029E,B18101_032E,B18101_035E,B18101_038E"
        urls["disability"] = f"https://api.census.gov/data/{year}/acs/acs5?get=NAME,B18101_001E,{dis_m},{dis_f}&for=county:{fips_str}&in=state:72&key={API_KEY}"
    else:
        urls["disability"] = f"https://api.census.gov/data/{year}/acs/acs5/subject?get=NAME,S1810_C02_001E&for=county:{fips_str}&in=state:72&key={API_KEY}"

    # --- 7. LIMITED ENGLISH (FINAL FIX) ---
    # Calc: (Total Spanish - Spanish "Very Well") = Vulnerable
    # B16002_003E (Total Spanish), B16002_004E (Spanish: Very Well)
    urls["language"] = f"https://api.census.gov/data/{year}/acs/acs5?get=NAME,B16002_001E,B16002_003E,B16002_004E&for=county:{fips_str}&in=state:72&key={API_KEY}"

    # --- 8. HOUSING & VEHICLES ---
    urls["housing"] = f"https://api.census.gov/data/{year}/acs/acs5?get=NAME,B25024_001E,B25024_010E,B25044_003E,B25044_010E,B25014_005E,B25014_006E,B25014_007E,B25014_011E,B25014_012E,B25014_013E&for=county:{fips_str}&in=state:72&key={API_KEY}"
    urls["structure"] = f"https://api.census.gov/data/{year}/acs/acs5?get=NAME,B25024_001E,B25024_006E,B25024_007E,B25024_008E&for=county:{fips_str}&in=state:72&key={API_KEY}"
    urls["gq"] = f"https://api.census.gov/data/{year}/acs/acs5?get=NAME,B26001_001E&for=county:{fips_str}&in=state:72&key={API_KEY}"


    # --- FETCH ---
    payloads = {}
    for k, u in urls.items():
        try:
            r = requests.get(u, timeout=30)
            if r.status_code == 200:
                data = r.json()
                header = data[0]
                s_idx = header.index("state")
                c_idx = header.index("county")
                payloads[k] = {f"{row[s_idx]}{row[c_idx]}": row for row in data[1:]}
        except Exception:
            continue

    # --- PROCESS ---
    for fips in PR_FIPS:
        geoid = f"72{fips}"
        if "poverty" not in payloads or geoid not in payloads["poverty"]: continue
        
        # Shortcuts
        pov = payloads["poverty"][geoid]
        inc = payloads.get("income", {}).get(geoid)
        dem = payloads.get("demographics", {}).get(geoid)
        single = payloads.get("single_parent", {}).get(geoid)
        edu = payloads.get("education", {}).get(geoid)
        emp = payloads.get("employment", {}).get(geoid)
        dis = payloads.get("disability", {}).get(geoid)
        lang = payloads.get("language", {}).get(geoid)
        hou = payloads.get("housing", {}).get(geoid)
        struc = payloads.get("structure", {}).get(geoid)
        gq = payloads.get("gq", {}).get(geoid)

        # 1. Poverty
        total_pop_pov = safe_float(pov[1])
        pov_rate = (safe_float(pov[2]) / total_pop_pov * 100) if total_pop_pov > 0 else 0

        # 2. Income
        per_capita = safe_float(inc[1]) if inc else 0

        # 3. Unemployment
        unemp_rate = (safe_float(emp[1]) / safe_float(emp[2]) * 100) if emp and safe_float(emp[2]) > 0 else 0

        # 4. No HS Diploma
        if edu:
            total_25plus = safe_float(edu[1])
            no_hs_count = sum([safe_float(x) for x in edu[2:]])
            no_hs_pct = (no_hs_count / total_25plus * 100) if total_25plus > 0 else 0
        else:
            no_hs_pct = 0

        # 5. Demographics
        if dem:
            total_pop = safe_float(dem[1])
            under_18 = sum([safe_float(x) for x in dem[4:12]])
            over_65 = sum([safe_float(x) for x in dem[12:]])
            under_18_pct = (under_18 / total_pop * 100) if total_pop > 0 else 0
            over_65_pct = (over_65 / total_pop * 100) if total_pop > 0 else 0
            
            min_base = safe_float(dem[2])
            minority_pct = ((min_base - safe_float(dem[3])) / min_base * 100) if min_base > 0 else 0
        else:
            under_18_pct, over_65_pct, minority_pct = 0, 0, 0

        # 6. Single Parent
        if single:
            sp_count = safe_float(single[1]) + safe_float(single[2])
            sp_pct = (sp_count / safe_float(single[3]) * 100) if safe_float(single[3]) > 0 else 0
        else:
            sp_pct = 0

        # 7. Disability (FIXED)
        if dis:
            if year < 2012:
                # Summing the 12 columns (Indices 2-13)
                dis_count = sum([safe_float(x) for x in dis[2:14]])
                total_dis_base = safe_float(dis[1])
                dis_pct = (dis_count / total_dis_base * 100) if total_dis_base > 0 else 0
            else:
                dis_count = safe_float(dis[1])
                dis_pct = (dis_count / total_pop * 100) if total_pop > 0 else 0
        else:
            dis_pct = 0

        # 8. Limited English (FIXED)
        if lang:
            # 003(Span Total) - 004(Span Very Well)
            span_total = safe_float(lang[2])
            span_well = safe_float(lang[3])
            lim_eng = max(0, span_total - span_well) # Ensure non-negative
            
            total_hh = safe_float(lang[1])
            lim_eng_pct = (lim_eng / total_hh * 100) if total_hh > 0 else 0
        else:
            lim_eng_pct = 0

        # 9. Housing
        if hou and struc:
            total_units = safe_float(struc[1])
            multi_count = safe_float(struc[2]) + safe_float(struc[3]) + safe_float(struc[4])
            multi_pct = (multi_count / total_units * 100) if total_units > 0 else 0
            mobile_pct = (safe_float(hou[2]) / total_units * 100) if total_units > 0 else 0 
            
            denom_hh = safe_float(single[3]) if single else total_units
            no_veh = safe_float(hou[3]) + safe_float(hou[4])
            no_veh_pct = (no_veh / denom_hh * 100) if denom_hh > 0 else 0
            
            crowd = sum([safe_float(x) for x in hou[5:]])
            crowd_pct = (crowd / denom_hh * 100) if denom_hh > 0 else 0
        else:
            multi_pct, mobile_pct, no_veh_pct, crowd_pct = 0, 0, 0, 0

        # 10. Group Quarters
        gq_count = safe_float(gq[1]) if gq else 0

        records.append({
            "year": year,
            "municipio": pov[0].replace(", Puerto Rico", ""),
            "geoid": geoid,
            "total_population": total_pop,
            "poverty_rate_pct": round(pov_rate, 2),
            "unemployment_rate_pct": round(unemp_rate, 2),
            "per_capita_income": per_capita,
            "no_hs_diploma_pct": round(no_hs_pct, 2),
            "under_18_pct": round(under_18_pct, 2),
            "over_65_pct": round(over_65_pct, 2),
            "disability_pct": round(dis_pct, 2),
            "single_parent_pct": round(sp_pct, 2),
            "minority_pct": round(minority_pct, 2),
            "limited_english_pct": round(lim_eng_pct, 2),
            "multi_unit_housing_pct": round(multi_pct, 2),
            "mobile_homes_pct": round(mobile_pct, 2),
            "crowding_pct": round(crowd_pct, 2),
            "no_vehicle_pct": round(no_veh_pct, 2),
            "group_quarters_count": gq_count
        })

# =============================
# 2. SAVE RESULTS
# =============================
df = pd.DataFrame(records).sort_values(["year", "municipio"])
csv_path = OUT / "puerto_rico_svi_data_2010_2024.csv"
df.to_csv(csv_path, index=False)
print(f"\n✅ SVI collection complete: {csv_path.name}")
