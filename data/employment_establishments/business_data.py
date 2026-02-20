import pandas as pd
import requests
import time
from pathlib import Path
import sys

# =============================
# CONFIGURATION
# =============================
API_KEY = "29dc42832697b740f9eff8ae8d61b9e544478c2b"
OUT = Path(__file__).resolve().parent
YEARS = range(2010, 2023)  # CBP Data is usually available up to 2022

# Puerto Rico FIPS Codes (All 78 Municipalities)
PR_FIPS = ['001','003','005','007','009','011','013','015','017','019','021','023','025','027',
           '029','031','033','035','037','039','041','043','045','047','049','051','053','054',
           '055','057','059','061','063','065','067','069','071','073','075','077','079','081',
           '083','085','087','089','091','093','095','097','099','101','103','105','107','109',
           '111','113','115','117','119','121','123','125','127','129','131','133','135','137',
           '139','141','143','145','147','149','151','153']

# NAICS Sector Codes (The "Kind" of Business)
SECTORS = {
    '00': 'Total_All_Sectors',
    '72': 'Tourism_Hospitality',    # Accommodation and Food Services
    '44-45': 'Retail_Trade',        # Shops / Stores
    '54': 'Professional_Services',  # Scientific, Tech, Consulting (LLCs)
    '62': 'Healthcare',             # Doctors, Social Assistance
    '23': 'Construction'            # Rebuilding / Contractors
}

def fetch_cbp_data(year):
    """
    Fetches County Business Patterns (CBP) data.
    Note: CBP endpoint structure changes slightly over years, this handles standard query.
    """
    print(f"📡 Fetching Business Data for {year}...")
    records = []
    
    # 1. Fetch Totals & Industry Breakdown
    # CBP API format: https://api.census.gov/data/{year}/cbp?get=ESTAB,NAICS2017&for=county:*&in=state:72
    # NAICS param name changes: NAICS2007 (2010-2011), NAICS2012 (2012-2016), NAICS2017 (2017+)
    
    if year < 2012: naics_code = "NAICS2007"
    elif year < 2017: naics_code = "NAICS2012"
    else: naics_code = "NAICS2017"
    
    url = f"https://api.census.gov/data/{year}/cbp?get=ESTAB,LFO,{naics_code}&for=county:*&in=state:72&key={API_KEY}"
    
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            print(f"   ⚠️ API Error {year}: {r.status_code}")
            return []
            
        data = r.json()
        header = data[0]
        
        # Parse the raw data into a dictionary for easier processing
        # Structure: {FIPS: {Sector: Count}}
        temp_storage = {}
        
        for row in data[1:]:
            fips = row[header.index("county")]
            estabs = int(row[header.index("ESTAB")])
            industry = row[header.index(naics_code)]
            
            # Filter for specific sectors we care about
            if industry in SECTORS:
                col_name = SECTORS[industry]
                if fips not in temp_storage: temp_storage[fips] = {}
                temp_storage[fips][col_name] = estabs

        # 2. Fetch Micro-Business Data (1-4 Employees)
        # We query for Legal Form of Organization or Employment Size Class if available
        # The easiest way to get size class is a separate query filtering by 'EMPSZES' (Employment Size of Establishment)
        # Code '210' = Less than 5 employees (Micro Business)
        
        size_url = f"https://api.census.gov/data/{year}/cbp?get=ESTAB&for=county:*&in=state:72&key={API_KEY}&EMPSZES=210"
        sr = requests.get(size_url, timeout=10)
        micro_data = {}
        if sr.status_code == 200:
            s_data = sr.json()
            s_header = s_data[0]
            for s_row in s_data[1:]:
                s_fips = s_row[s_header.index("county")]
                micro_data[s_fips] = int(s_row[s_header.index("ESTAB")])
        
        # 3. Assemble Final Records
        for fips in PR_FIPS:
            if fips in temp_storage:
                row = temp_storage[fips]
                row['year'] = year
                row['municipio_fips'] = f"72{fips}"
                
                # Add Micro-Business Count
                row['Micro_Businesses_1to4_Employees'] = micro_data.get(fips, 0)
                
                # Calculate "Small Business Share"
                total = row.get('Total_All_Sectors', 0)
                if total > 0:
                    row['Pct_Micro_Business'] = round((row['Micro_Businesses_1to4_Employees'] / total) * 100, 1)
                else:
                    row['Pct_Micro_Business'] = 0
                
                records.append(row)
                
    except Exception as e:
        print(f"   ❌ Critical Error {year}: {e}")
        
    return records

# =============================
# MAIN LOOP
# =============================
all_records = []

print("🚀 Starting Deep Dive Business Data Collection (2010-2022)...")
for year in YEARS:
    year_data = fetch_cbp_data(year)
    all_records.extend(year_data)
    time.sleep(1) # Be nice to the API

# =============================
# SAVE
# =============================
if all_records:
    df = pd.DataFrame(all_records)
    
    # Reorder columns nicely
    cols = ['year', 'municipio_fips', 'Total_All_Sectors', 'Micro_Businesses_1to4_Employees', 'Pct_Micro_Business']
    # Add sector columns dynamically if they exist
    for sec in SECTORS.values():
        if sec != 'Total_All_Sectors' and sec in df.columns:
            cols.append(sec)
            
    df = df[cols].sort_values(['year', 'municipio_fips'])
    
    filename = "puerto_rico_business_deep_dive_2010_2022.csv"
    df.to_csv(OUT / filename, index=False)
    print(f"\n✅ SUCCESS! Saved {filename}")
    print(df.head())
else:
    print("\n❌ Failed to collect data.")
