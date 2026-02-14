import os
import pandas as pd
import json

# ==========================================
# 1. SETUP & CONFIGURATION
# ==========================================
# Force Python to work in the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
print(f"Running in: {script_dir}")

file_name = "PR_Crime_Summary_2010_2025.xlsx"
output_file = "crime_data.json"

if not os.path.exists(file_name):
    print(f"ERROR: '{file_name}' not found.")
    exit()

# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================
def clean_header(header):
    """Standardizes column names (e.g., 'TOTAL' -> 'Total')."""
    header = str(header).strip()
    if header.upper() == "TOTAL":
        return "Total"
    if header.upper() == "MUNICIPIO":
        return "Municipio"
    return header

def clean_number(value):
    """
    Fixes the 2025 formatting issue where 1,000 is written as 1.000
    Interprets dots/commas as thousand separators, not decimals.
    """
    if pd.isna(value) or str(value).strip() == "":
        return 0
    
    # Convert to string first
    s_val = str(value).strip()
    
    # Remove BOTH dots and commas
    # Example: "1.154" -> "1154"
    # Example: "1,154" -> "1154"
    s_val = s_val.replace('.', '').replace(',', '')
    
    try:
        # Convert to integer
        return int(float(s_val))
    except ValueError:
        return 0

# ==========================================
# 3. PROCESSING
# ==========================================
try:
    print("Reading Excel file (all tabs)...")
    # Read as String (dtype=str) to prevent Pandas from guessing 
    # wrongly about the dot vs comma issue before we clean it.
    all_sheets = pd.read_excel(file_name, sheet_name=None, dtype=str)
    
    master_data = []
    
    for sheet_name, df in all_sheets.items():
        if "Legend" in sheet_name:
            continue
            
        print(f"Processing Year: {sheet_name}...")
        
        # 1. Standardize Column Headers
        df.columns = [clean_header(c) for c in df.columns]
        
        # Identify which columns are stats (everything except Municipio)
        # We only want to clean columns that actually exist in this sheet
        stat_cols = [c for c in df.columns if c != "Municipio"]
        
        # 2. Iterate through rows
        for _, row in df.iterrows():
            record = {}
            
            # Skip empty rows
            if pd.isna(row.get("Municipio")):
                continue

            # Clean Municipio Name (ADJUNTAS -> Adjuntas)
            record["Municipio"] = str(row["Municipio"]).strip().title()
            
            # Add Year
            record["Year"] = str(sheet_name)
            
            # Clean Numeric Data
            for col in stat_cols:
                record[col] = clean_number(row.get(col, 0))
            
            master_data.append(record)

    # ==========================================
    # 4. SAVE TO JSON
    # ==========================================
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(master_data, f, indent=4, ensure_ascii=False)
        
    print(f"\nSUCCESS! Processed {len(master_data)} records.")
    print(f"Saved to: {os.path.join(script_dir, output_file)}")
    
    # Validation Check
    # Check a 2025 record to ensure 'Total' is not tiny (e.g. 1.898)
    sample_2025 = next((d for d in master_data if d['Year'] == '2025' and d['Total'] > 100), None)
    if sample_2025:
        print(f"Verification (2025 Data): {sample_2025['Municipio']} Total Crime = {sample_2025['Total']}")
    else:
        print("WARNING: 2025 data still looks small. Check the source file.")

except Exception as e:
    print(f"\nCRITICAL ERROR: {e}")
    print("Make sure to run: pip install pandas openpyxl")
