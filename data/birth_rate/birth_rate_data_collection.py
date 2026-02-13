# birth_rate_collection_fixed.py
import ssl
import pandas as pd
import requests
import sys
from pathlib import Path

# SSL Fix
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Config
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
        return float(val)
    except (ValueError, TypeError):
        return 0.0

print("\n👶 Collecting CORRECTED Birth Statistics (2010–2024)...")
records = []
years = range(2010, 2025)
fips_str = ",".join(PR_FIPS)

for year in years:
    sys.stdout.write(f"\rProcessing Year: {year} ...")
    sys.stdout.flush()

    # B01001_001E: Total Population
    # B13016_002E: Women 15-50 who had a birth in past 12 months (CORRECT VARIABLE)
    url = f"https://api.census.gov/data/{year}/acs/acs5?get=NAME,B01001_001E,B13016_002E&for=county:{fips_str}&in=state:72&key={API_KEY}"

    try:
        r = requests.get(url, timeout=30)
        if r.status_code == 200:
            data = r.json()
            header = data[0]
            name_idx = header.index("NAME")
            pop_idx = header.index("B01001_001E")
            birth_idx = header.index("B13016_002E") # Index for the correct variable
            state_idx = header.index("state")
            county_idx = header.index("county")

            for row in data[1:]:
                total_pop = safe_float(row[pop_idx])
                total_births = safe_float(row[birth_idx])
                
                # Crude Birth Rate = (Births / Pop) * 1000
                birth_rate = (total_births / total_pop * 1000) if total_pop > 0 else 0.0
                
                records.append({
                    "year": year,
                    "municipio": row[name_idx].replace(", Puerto Rico", ""),
                    "geoid": f"{row[state_idx]}{row[county_idx]}",
                    "total_population": total_pop,
                    "total_births_est": total_births,
                    "crude_birth_rate": round(birth_rate, 2)
                })
    except Exception as e:
        continue

df = pd.DataFrame(records).sort_values(["year", "municipio"])
csv_path = OUT / "puerto_rico_birth_statistics_2010_2024.csv"
df.to_csv(csv_path, index=False)
print(f"\n✅ Corrected data saved: {csv_path.name}")
