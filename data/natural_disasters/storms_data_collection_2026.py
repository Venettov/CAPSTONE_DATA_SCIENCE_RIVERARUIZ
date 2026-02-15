import requests
import re
import json
import csv
import pandas as pd
import os
from bs4 import BeautifulSoup 

# ------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------
JSON_OUTPUT = "caribbean_hurricane_tracks_2010_2025.json"
CSV_OUTPUT  = "caribbean_hurricane_tracks_2010_2025.csv"

# NOAA Data Settings
DIRECT_URL = "https://www.nhc.noaa.gov/data/hurdat/hurdat2-1851-2023-051124.txt"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
}

def get_hurdat2_link():
    try:
        r = requests.get("https://www.nhc.noaa.gov/data/", headers=HEADERS, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.find_all("a", href=True):
            if "hurdat2" in a['href'] and a['href'].endswith(".txt") and "atlantic" in a['href'].lower():
                return requests.compat.urljoin("https://www.nhc.noaa.gov/data/", a['href'])
    except:
        pass
    return DIRECT_URL

def collect_data():
    url = get_hurdat2_link()
    print(f"⬇️ Downloading from {url}...")
    raw_text = requests.get(url, headers=HEADERS, timeout=30).text

    print("⚡ Processing Storms...")
    storms = []
    lines = raw_text.splitlines()
    current_storm = None
    header_pattern = re.compile(r"^([A-Z]{2}\d{6}),\s*([A-Z\d\s]+),\s*(\d+),")

    for line in lines:
        line = line.strip()
        if not line: continue
        match = header_pattern.match(line)
        if match:
            if current_storm: storms.append(current_storm)
            storm_id = match.group(1)
            current_storm = {"id": storm_id, "name": match.group(2).strip(), "year": int(storm_id[4:]), "records": []}
        else:
            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 20: continue
            try:
                lat = float(parts[4][:-1]) * (-1 if "S" in parts[4] else 1)
                lon = float(parts[5][:-1]) * (-1 if "W" in parts[5] else 1)
                current_storm['records'].append({
                    "date": f"{parts[0][:4]}-{parts[0][4:6]}-{parts[0][6:8]}",
                    "time": parts[1],
                    "lat": lat,
                    "lon": lon,
                    "wind_knots": int(parts[6]),
                    "pressure_mb": int(parts[7]) if parts[7] != "-999" else None,
                    "r34": [int(parts[8]), int(parts[9]), int(parts[10]), int(parts[11])],
                    "r50": [int(parts[12]), int(parts[13]), int(parts[14]), int(parts[15])],
                    "r64": [int(parts[16]), int(parts[17]), int(parts[18]), int(parts[19])]
                })
            except: continue
    if current_storm: storms.append(current_storm)

    # Filter for Caribbean (2010-2025)
    final_data = []
    for s in storms:
        if 2010 <= s['year'] <= 2025:
            # Caribbean check
            if any(10.0 <= r['lat'] <= 24.0 and -85.0 <= r['lon'] <= -60.0 for r in s['records']):
                final_data.append({
                    "id": s['id'],
                    "name": s['name'],
                    "year": s['year'],
                    "path": s['records'] # HTML expects "path"
                })

    # Save JSON
    with open(JSON_OUTPUT, "w") as f:
        json.dump(final_data, f, indent=2)
    print(f"✅ JSON Generated: {JSON_OUTPUT}")

    # Save CSV (Flattened)
    with open(CSV_OUTPUT, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['Storm_ID','Name','Year','Date','Lat','Lon','Wind_Knots','Pressure_mb','R34_NE','R34_SE','R34_SW','R34_NW','R64_NE','R64_SE','R64_SW','R64_NW'])
        for s in final_data:
            for r in s['path']:
                w.writerow([s['id'], s['name'], s['year'], r['date'], r['lat'], r['lon'], r['wind_knots'], r['pressure_mb'], *r['r34'], *r['r64']])
    print(f"✅ CSV Generated: {CSV_OUTPUT}")

if __name__ == "__main__":
    collect_data()
