import pandas as pd
import numpy as np

# Create a sample population dataset
np.random.seed(42)
n_citizens = 1600

ages = np.random.randint(20, 81, n_citizens)
sexes = np.random.choice(["M", "F"], n_citizens)

# Diseases - top 15
diseases = [
    "Obesity",
    "Hypercholesterolemia",
    "Osteoarthritis",
    "Hypertension",
    "Allergy",
    "Focal thyroid lesions",
    "Lower limb varicose veins",
    "Rectal varices",
    "Hypertriglyceridemia",
    "Gastroesophageal reflux disease",
    "Peptic ulcer disease",
    "Discopathy",
    "Migraine",
    "Cholelithiasis",
    "Fatty liver disease",
]

# Disease prevalence rates
prevalence = {
    "Obesity": 0.44,
    "Hypercholesterolemia": 0.33,
    "Osteoarthritis": 0.305,
    "Hypertension": 0.285,
    "Allergy": 0.22,
    "Focal thyroid lesions": 0.181,
    "Lower limb varicose veins": 0.177,
    "Rectal varices": 0.177,
    "Hypertriglyceridemia": 0.171,
    "Gastroesophageal reflux disease": 0.148,
    "Peptic ulcer disease": 0.121,
    "Discopathy": 0.117,
    "Migraine": 0.109,
    "Cholelithiasis": 0.101,
    "Fatty liver disease": 0.092,
}

data = {
    "id": range(1, n_citizens + 1),
    "sex": sexes,
    "age": ages,
    "household_id": np.random.randint(1, 400, n_citizens),
    "zone_id": np.random.randint(1, 4, n_citizens),
}

# Add disease columns
for disease in diseases:
    prob = prevalence[disease]
    # Increase prevalence with age
    age_factor = 1 + (ages - 50) / 100
    age_factor = np.clip(age_factor, 0.3, 1.5)
    prob_by_age = prob * age_factor
    data[disease] = np.random.binomial(1, prob_by_age)

df = pd.DataFrame(data)

# Save to Excel
output_file = "population_data.xlsx"
df.to_excel(output_file, index=False)
print(f"Created population dataset: {output_file}")
print(f"Shape: {df.shape}")
print(f"\nFirst 5 rows:")
print(df.head())
print(f"\nColumns: {list(df.columns)}")
