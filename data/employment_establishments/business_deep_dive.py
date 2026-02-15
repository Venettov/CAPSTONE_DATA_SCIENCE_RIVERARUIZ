import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Load the Data
try:
    # Ensure this matches the filename you generated with the collection script
    bus_df = pd.read_csv('puerto_rico_business_deep_dive_2010_2022.csv')
    pop_df = pd.read_csv('puerto_rico_master_profile_2010_2024.csv') # Needed for the population line
    print("✅ Data Loaded Successfully!")
except FileNotFoundError:
    print("❌ Error: Files not found. Make sure both CSVs are in the same folder.")
    # Stop execution if data is missing
    exit()

# 2. Aggregate Data by Year (Island-Wide Totals)
bus_trend = bus_df.groupby('year')[['Total_All_Sectors', 'Micro_Businesses_1to4_Employees', 
                                    'Professional_Services', 'Tourism_Hospitality', 'Retail_Trade']].sum().reset_index()

# Get Population Trend (Filter for matching years)
pop_trend = pop_df.groupby('year')['total_population'].sum().reset_index()
merged = pd.merge(bus_trend, pop_trend, on='year')

# ==========================================
# CHART 1: The "Paradox" (Population vs. Business)
# ==========================================
fig, ax1 = plt.subplots(figsize=(12, 6))

color = 'tab:red'
ax1.set_xlabel('Year', fontsize=12)
ax1.set_ylabel('Total Population (Millions)', color=color, fontsize=12)
ax1.plot(merged['year'], merged['total_population'], color=color, linewidth=3, marker='o', label='Population (Left)')
ax1.tick_params(axis='y', labelcolor=color)
ax1.grid(False)

ax2 = ax1.twinx()
color = 'tab:blue'
ax2.set_ylabel('Total Business Establishments', color=color, fontsize=12)
ax2.plot(merged['year'], merged['Total_All_Sectors'], color=color, linewidth=3, linestyle='--', marker='s', label='Businesses (Right)')
ax2.tick_params(axis='y', labelcolor=color)

plt.title('The Puerto Rico Paradox: Declining Population vs. Rising Businesses', fontsize=14, fontweight='bold')
fig.tight_layout()
plt.show()

# ==========================================
# CHART 2: The "Micro-Business" Driver
# ==========================================
merged['Micro_Share'] = (merged['Micro_Businesses_1to4_Employees'] / merged['Total_All_Sectors']) * 100

plt.figure(figsize=(12, 6))
# FIXED: Added hue='year' and legend=False to silence the warning
sns.barplot(data=merged, x='year', y='Micro_Share', hue='year', legend=False, palette='Blues_d')
plt.ylim(50, 75)
plt.title('Rise of the "Solopreneur": Micro-Businesses (1-4 Employees) as % of Total', fontsize=14, fontweight='bold')
plt.ylabel('Percentage of Total Establishments')
plt.axhline(merged['Micro_Share'].mean(), color='red', linestyle='--', label='Average')
plt.show()

# ==========================================
# CHART 3: Sector Shift (Retail vs. Prof Services)
# ==========================================
base_2012 = merged[merged['year'] == 2012].iloc[0]

merged['Idx_Professional'] = (merged['Professional_Services'] / base_2012['Professional_Services']) * 100
merged['Idx_Tourism'] = (merged['Tourism_Hospitality'] / base_2012['Tourism_Hospitality']) * 100
merged['Idx_Retail'] = (merged['Retail_Trade'] / base_2012['Retail_Trade']) * 100

plt.figure(figsize=(12, 6))
plt.plot(merged['year'], merged['Idx_Professional'], label='Professional Services (Consulting/LLCs)', linewidth=3, color='purple')
plt.plot(merged['year'], merged['Idx_Tourism'], label='Tourism & Hospitality', linewidth=3, color='orange')
plt.plot(merged['year'], merged['Idx_Retail'], label='Retail Trade (Physical Stores)', linewidth=3, color='gray', linestyle='--')

plt.axhline(100, color='black', linewidth=1)
plt.title('Sector Growth Index (2012 = 100)', fontsize=14, fontweight='bold')
plt.ylabel('Growth Index (100 = No Change)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()
