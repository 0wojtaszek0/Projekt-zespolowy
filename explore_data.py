import pandas as pd
import re

file_path = "jcm-2565714-supplementary.xlsx"
df = pd.read_excel(file_path, sheet_name=0, header=None)

diseases = []

# Start from row 5 (index 5) where disease data begins
for idx in range(5, len(df)):
    disease_name = df.iloc[idx, 1]  # Column 1
    disease_data = df.iloc[idx, 2]  # Column 2 has "count (%)"
    
    if pd.isna(disease_name) or not isinstance(disease_name, str):
        continue
    if pd.isna(disease_data) or not isinstance(disease_data, str):
        continue
    
    # Extract percentage
    match = re.search(r'(\d+)\s*\((\d+\.?\d*)%\)', str(disease_data))
    if match:
        count = int(match.group(1))
        percentage = float(match.group(2))
        diseases.append({
            'name': disease_name.strip(),
            'count': count,
            'percentage': percentage
        })

# Sort by percentage descending
diseases.sort(key=lambda x: x['percentage'], reverse=True)

print("=" * 60)
print("EXTRACTED DISEASES")
print("=" * 60)
for i, d in enumerate(diseases, 1):
    print(f"{i:2}. {d['name']:<35} {d['count']:>4} ({d['percentage']:>5.1f}%)")

print("\n" + "=" * 60)
print(f"Total diseases found: {len(diseases)}")
print("=" * 60)

# Select top 15
top_15 = diseases[:15]
print("\nTOP 15 DISEASES FOR SIMULATION:")
print("-" * 60)
for i, d in enumerate(top_15, 1):
    print(f"{i:2}. {d['name']:<35} {d['percentage']:>6.1f}%")
