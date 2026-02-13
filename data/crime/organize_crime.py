import os
import zipfile
import re
from pathlib import Path

# =================CONFIGURATION =================
SOURCE_DIR = "zipped_data"
DEST_DIR = "crime2010-2024"

# Map everything to a simple "01", "02", "12" string
MONTH_MAP = {
    # Numbers
    "1": "01", "01": "01",
    "2": "02", "02": "02",
    "3": "03", "03": "03",
    "4": "04", "04": "04",
    "5": "05", "05": "05",
    "6": "06", "06": "06",
    "7": "07", "07": "07",
    "8": "08", "08": "08",
    "9": "09", "09": "09",
    "10": "10",
    "11": "11",
    "12": "12",
    # Spanish Names
    "enero": "01", "febrero": "02", "marzo": "03",
    "abril": "04", "mayo": "05", "junio": "06",
    "julio": "07", "agosto": "08", "septiembre": "09",
    "octubre": "10", "noviembre": "11", "diciembre": "12",
    # English Names
    "january": "01", "february": "02", "march": "03",
    "april": "04", "may": "05", "june": "06",
    "july": "07", "august": "08", "september": "09",
    "october": "10", "november": "11", "december": "12"
}

def parse_date(filename):
    """
    Returns (Year, Month_Code) e.g., ('2010', '01')
    """
    fn_clean = filename.lower().replace(" ", "-")

    # PATTERN 1: "YYYY-MM" or "YYYY_MM"
    match = re.search(r"(20[0-2][0-9])[-_](\d{1,2})", fn_clean)
    if match:
        year, month = match.groups()
        if 1 <= int(month) <= 12:
            return year, MONTH_MAP.get(str(int(month)), "00")

    # PATTERN 2: Compact "YYYYMM"
    match_compact = re.search(r"(20[0-2][0-9])(\d{2})", fn_clean)
    if match_compact:
        year, month = match_compact.groups()
        if 1 <= int(month) <= 12:
            return year, MONTH_MAP.get(str(int(month)), "00")

    # PATTERN 3: Month Name and Year
    year_match = re.search(r"(20[0-2][0-9])", fn_clean)
    if year_match:
        year = year_match.group(1)
        for key in MONTH_MAP:
            if key.isalpha() and key in fn_clean:
                return year, MONTH_MAP[key]
    
    return None

def main():
    base_path = Path(__file__).parent
    src_path = base_path / SOURCE_DIR
    dest_path = base_path / DEST_DIR

    if not src_path.exists():
        print(f"❌ Error: Folder '{SOURCE_DIR}' not found.")
        return

    dest_path.mkdir(exist_ok=True)
    print(f"📂 Scanning '{SOURCE_DIR}'...")
    
    count = 0
    errors = 0

    for file_path in src_path.glob("*.zip"):
        filename = file_path.name
        
        date_info = parse_date(filename)
        
        if date_info:
            year, month_code = date_info
            # FOLDER NAMING: 2010_01
            folder_name = f"{year}_{month_code}"
            target_dir = dest_path / folder_name
            display_info = folder_name
        else:
            print(f"   ⚠️  Could not identify date: {filename} -> Moving to 'Unsorted'")
            target_dir = dest_path / "Unsorted" / filename.replace(".zip", "")
            display_info = "Unsorted"
            
        target_dir.mkdir(parents=True, exist_ok=True)

        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(target_dir)
                print(f"   ✅ Unzipped: {filename} -> {display_info}")
                count += 1
        except zipfile.BadZipFile:
            print(f"   ❌ Error: {filename} is corrupted.")
            errors += 1
        except Exception as e:
            print(f"   ❌ Error on {filename}: {e}")
            errors += 1

    print("\n" + "="*40)
    print(f"🎉 Done! Extracted {count} folders.")
    print(f"📁 Data organized in: {dest_path}")

if __name__ == "__main__":
    main()
