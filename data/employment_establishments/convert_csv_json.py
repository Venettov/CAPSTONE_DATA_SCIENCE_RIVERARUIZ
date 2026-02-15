import pandas as pd
import json

# 1. Load the CSV File
# Replace with your actual file path
csv_file_path = 'puerto_rico_business_deep_dive_2010_2022.csv' 
df = pd.read_csv(csv_file_path)

# 2. FIPS to Municipality Name Mapping
# Standard PR FIPS codes (Alphabetical order, odd numbers)
fips_map = {
    72001: "Adjuntas", 72003: "Aguada", 72005: "Aguadilla", 72007: "Aguas Buenas", 
    72009: "Aibonito", 72011: "Añasco", 72013: "Arecibo", 72015: "Arroyo", 
    72017: "Barceloneta", 72019: "Barranquitas", 72021: "Bayamón", 72023: "Cabo Rojo", 
    72025: "Caguas", 72027: "Camuy", 72029: "Canóvanas", 72031: "Carolina", 
    72033: "Cataño", 72035: "Cayey", 72037: "Ceiba", 72039: "Ciales", 
    72041: "Cidra", 72043: "Coamo", 72045: "Comerío", 72047: "Corozal", 
    72049: "Culebra", 72051: "Dorado", 72053: "Fajardo", 72054: "Florida", 
    72055: "Guánica", 72057: "Guayama", 72059: "Guayanilla", 72061: "Guaynabo", 
    72063: "Gurabo", 72065: "Hatillo", 72067: "Hormigueros", 72069: "Humacao", 
    72071: "Isabela", 72073: "Jayuya", 72075: "Juana Díaz", 72077: "Juncos", 
    72079: "Lajas", 72081: "Lares", 72083: "Las Marías", 72085: "Las Piedras", 
    72087: "Loíza", 72089: "Luquillo", 72091: "Manatí", 72093: "Maricao", 
    72095: "Maunabo", 72097: "Mayagüez", 72099: "Moca", 72101: "Morovis", 
    72103: "Naguabo", 72105: "Naranjito", 72107: "Orocovis", 72109: "Patillas", 
    72111: "Peñuelas", 72113: "Ponce", 72115: "Quebradillas", 72117: "Rincón", 
    72119: "Río Grande", 72121: "Sabana Grande", 72123: "Salinas", 72125: "San Germán", 
    72127: "San Juan", 72129: "San Lorenzo", 72131: "San Sebastián", 72133: "Santa Isabel", 
    72135: "Toa Alta", 72137: "Toa Baja", 72139: "Trujillo Alto", 72141: "Utuado", 
    72143: "Vega Alta", 72145: "Vega Baja", 72147: "Vieques", 72149: "Villalba", 
    72151: "Yabucoa", 72153: "Yauco"
}

# Apply Mapping
df['Municipio'] = df['municipio_fips'].map(fips_map)

# 3. Define the Sector Columns you want to include
sector_cols = [
    'Tourism_Hospitality', 
    'Retail_Trade', 
    'Professional_Services', 
    'Healthcare', 
    'Construction',
    'Micro_Businesses_1to4_Employees' # Optional: Add this if you want it
]

# 4. Pivot Data to Wide Format
# Group by Municipio and create a dictionary for each
output_data = []

for municipio, group in df.groupby('Municipio'):
    record = {"Municipio": municipio}
    
    for _, row in group.iterrows():
        year = str(int(row['year']))
        
        # A. Base Metric: Total All Sectors (For Map Coloring/Lines)
        # Note: Keeps existing format: "2012": 123
        record[year] = int(row['Total_All_Sectors']) if pd.notna(row['Total_All_Sectors']) else 0
        
        # B. New Metrics: Sectors (For Bar Charts)
        # Format: "2012_Retail_Trade": 45
        for col in sector_cols:
            key_name = f"{year}_{col}"
            record[key_name] = int(row[col]) if pd.notna(row[col]) else 0

    output_data.append(record)

# 5. Save to JSON
output_filename = 'establishments_with_sectors.json'
with open(output_filename, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=4)

print(f"Success! JSON saved as '{output_filename}' with {len(output_data)} records.")
print("Sample Record Keys:", list(output_data[0].keys())[:10])
