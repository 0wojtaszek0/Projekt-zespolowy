"""
Comparison: Test Data (1k agents, 10 years) vs Full Simulation (50k agents, 50 years)
"""
import json
import pandas as pd

# Load both datasets
with open('gridsearch_results_v2_20260413_152309.json', 'r') as f:
    test_raw = json.load(f)

with open('gridsearch_results_full_50k_50y.json', 'r') as f:
    full_data = json.load(f)

# Convert test data to match structure
test_data = []
for entry in test_raw:
    test_data.append({
        'birth_rate': entry['params']['birth_rate'],
        'mortality_rate': entry['params']['mortality_rate'],
        'score': entry['score'],
        'combo': entry['combo']
    })

df_test = pd.DataFrame(test_data)
df_full = pd.DataFrame(full_data)

print("="*80)
print("PORÓWNANIE: Test Data vs Full Simulation")
print("="*80)

print(f"\n📊 TEST DATA (1,000 agentów, 10 lat):")
print(f"   Score range: {df_test['score'].min():+7.2f}% do {df_test['score'].max():+7.2f}%")
print(f"   Mean score: {df_test['score'].mean():+7.2f}%")
optimal_test = df_test.loc[df_test['score'].idxmax()]
print(f"   🏆 Optimal: BR={optimal_test['birth_rate']:.4f}, MR={optimal_test['mortality_rate']:.6f}")
print(f"      Score: {optimal_test['score']:+7.2f}%")

print(f"\n📊 FULL SIMULATION (50,000 agentów, 50 lat):")
print(f"   Score range: {df_full['score'].min():+7.2f}% do {df_full['score'].max():+7.2f}%")
print(f"   Mean score: {df_full['score'].mean():+7.2f}%")
optimal_full = df_full.loc[df_full['score'].idxmax()]
print(f"   🏆 Optimal: BR={optimal_full['birth_rate']:.4f}, MR={optimal_full['mortality_rate']:.6f}")
print(f"      Score: {optimal_full['score']:+7.2f}%")
print(f"      Pop: {optimal_full['initial_population']:.0f} → {optimal_full['final_population']:.0f}")

print("\n" + "="*80)
print("KEY DIFFERENCES:")
print("="*80)

# Create merge for comparison
df_merged = pd.merge(
    df_test[['birth_rate', 'mortality_rate', 'score']].rename(columns={'score': 'score_test'}),
    df_full[['birth_rate', 'mortality_rate', 'score']].rename(columns={'score': 'score_full'}),
    on=['birth_rate', 'mortality_rate']
)
df_merged['delta'] = df_merged['score_full'] - df_merged['score_test']

print(f"\n1️⃣  MAGNITUDE OF CHANGE:")
print(f"   Min delta:  {df_merged['delta'].min():+7.2f}%")
print(f"   Max delta:  {df_merged['delta'].max():+7.2f}%")
print(f"   Mean delta: {df_merged['delta'].mean():+7.2f}%")

print(f"\n2️⃣  SIGN FLIP ANALYSIS:")
positive_test = (df_test['score'] > 0).sum()
positive_full = (df_full['score'] > 0).sum()
print(f"   Test data positive scores: {positive_test}/25 combos")
print(f"   Full sim positive scores:  {positive_full}/25 combos")

print(f"\n3️⃣  OPTIMAL CONFIGURATION COMPARISON:")
if abs(optimal_test['birth_rate'] - optimal_full['birth_rate']) < 0.001:
    print(f"   ✅ SAME BIRTH RATE: {optimal_test['birth_rate']:.4f}")
else:
    print(f"   ❌ Different BR: Test={optimal_test['birth_rate']:.4f}, Full={optimal_full['birth_rate']:.4f}")

if abs(optimal_test['mortality_rate'] - optimal_full['mortality_rate']) < 0.00001:
    print(f"   ✅ SAME MORTALITY RATE: {optimal_test['mortality_rate']:.6f}")
else:
    print(f"   ❌ Different MR: Test={optimal_test['mortality_rate']:.6f}, Full={optimal_full['mortality_rate']:.6f}")

print(f"\n4️⃣  PARAMETER SENSITIVITY (Test vs Full):")
print(f"\n   Birth Rate Impact:")
df_br = df_merged.groupby('birth_rate')[['score_test', 'score_full']].mean()
for br, row in df_br.iterrows():
    print(f"      BR={br:.4f}: Test={row['score_test']:+6.2f}%, Full={row['score_full']:+6.2f}%")

print(f"\n   Mortality Rate Impact:")
df_mr = df_merged.groupby('mortality_rate')[['score_test', 'score_full']].mean()
for mr, row in df_mr.iterrows():
    print(f"      MR={mr:.6f}: Test={row['score_test']:+6.2f}%, Full={row['score_full']:+6.2f}%")

print("\n" + "="*80)
print("INTERPRETATION:")
print("="*80)
print(f"""
Test Data (1k, 10y):
  - Short timeframe reveals acute effects
  - Small population shows some volatility
  - Optimal uses max birth rate and min mortality
  - Best score only +1.30%

Full Simulation (50k, 50y):
  - Long timeframe reveals cumulative effects
  - Large population shows clear trends
  - Consistent pattern: higher BR always better
  - All 25 combos POSITIVE (lowest +4.67%)
  - Best score +45.48%

Why the difference?
  ✅ Time horizon: 50 years > 10 years
  ✅ Population size: 50k > 1k stabilizes outcomes
  ✅ Feedback loops: Long-term aging effects
  ✅ Mortality rate: Less critical over 50 years
     (birth rate gains accumulate over time)

RECOMMENDATION:
  Use parameters that maximize birth rate (BR=0.06)
  Mortality rate less critical (0.0005-0.003 all good)
  Expected population growth: +45-46% over 50 years
""")
