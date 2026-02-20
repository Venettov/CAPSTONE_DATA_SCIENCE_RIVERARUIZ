import requests
import pandas as pd
from pathlib import Path

def get_pr_vital_rates():
    # World Bank API indicators for Crude Birth/Death Rates (per 1,000 people)
    print("🌍 Fetching Puerto Rico macro vital rates from the World Bank API...")
    
    birth_url = "http://api.worldbank.org/v2/country/PRI/indicator/SP.DYN.CBRT.IN?format=json&per_page=50"
    death_url = "http://api.worldbank.org/v2/country/PRI/indicator/SP.DYN.CDRT.IN?format=json&per_page=50"
    
    try:
        b_resp = requests.get(birth_url).json()
        d_resp = requests.get(death_url).json()
        
        # Parse the JSON response
        birth_data = {item['date']: item['value'] for item in b_resp[1] if item['value'] is not None}
        death_data = {item['date']: item['value'] for item in d_resp[1] if item['value'] is not None}
        
        # Combine into a clean dataset
        records = []
        for year in range(2010, 2024):
            y_str = str(year)
            if y_str in birth_data and y_str in death_data:
                records.append({
                    "Year": year,
                    "Birth Rate (per 1k)": round(birth_data[y_str], 2),
                    "Death Rate (per 1k)": round(death_data[y_str], 2),
                    "Natural Change Rate": round(birth_data[y_str] - death_data[y_str], 2)
                })
                
        # Sort chronologically
        df = pd.DataFrame(records).sort_values("Year", ascending=False).reset_index(drop=True)
        
        # Save to CSV
        out_path = Path(__file__).resolve().parent / "pr_islandwide_vital_rates.csv"
        df.to_csv(out_path, index=False)
        
        print("\n📊 Puerto Rico Island-Wide Vital Trends:")
        print("-" * 55)
        print(df.to_string(index=False))
        print("-" * 55)
        print(f"\n✅ Saved successfully to '{out_path.name}'")

    except Exception as e:
        print(f"❌ API Error: {e}")

if __name__ == "__main__":
    get_pr_vital_rates()
