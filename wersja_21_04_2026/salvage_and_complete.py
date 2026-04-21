"""
Extract results from log file and generate JSON, then run remaining combos
"""
import json
import re
from simulation_engine import SimulationEngine
from disease_model import DiseaseModel

# Parse log file
results = []
with open('simulation_progress.log', 'r') as f:
    for line in f:
        # Pattern: [20/25] BR=0.0475, MR=0.003000 | Pop:  49995 →  66103 | Score:  +32.22% | Time:  58.0s
        match = re.search(r'\[(\d+)/25\]\s+BR=([\d.]+),\s+MR=([\d.]+)\s+\|\s+Pop:\s+(\d+)\s+→\s+(\d+)\s+\|\s+Score:\s+([\+\-\d.]+)%', line)
        if match:
            combo, br, mr, init_pop, final_pop, score = match.groups()
            results.append({
                'combo': int(combo),
                'birth_rate': float(br),
                'mortality_rate': float(mr),
                'initial_population': int(init_pop),
                'final_population': int(final_pop),
                'score': float(score),
                'elapsed_seconds': 0  # Not tracked in log
            })

print(f"Loaded {len(results)}/25 results from log file")

# Run remaining combos (22-25)
birth_rates = [0.01, 0.0225, 0.035, 0.0475, 0.06]
mortality_rates = [0.0005, 0.001125, 0.00175, 0.002375, 0.003]

completed_combos = {r['combo'] for r in results}

# Generate all possible combos
all_combos = []
for br in birth_rates:
    for mr in mortality_rates:
        combo_num = len(all_combos) + 1
        all_combos.append((br, mr, combo_num))

# Find remaining
remaining_combos = [(br, mr, combo_num) for br, mr, combo_num in all_combos 
                    if combo_num not in completed_combos]

print(f"\nRunning {len(remaining_combos)} remaining combos: {[c[2] for c in remaining_combos]}")

import time
for br, mr, combo_num in remaining_combos:
    combo_start = time.time()
    try:
        print(f"\n[{combo_num}/25] BR={br:.4f}, MR={mr:.6f}...", flush=True)
        
        disease_model = DiseaseModel()
        engine = SimulationEngine(disease_model=disease_model, seed=42)
        
        scaled_fertility_table = {
            age: rate * br / 0.03
            for age, rate in engine.DEFAULT_FERTILITY_TABLE.items()
        }
        
        scaled_mortality_table = {
            age: (male_rate * mr / 0.0015, female_rate * mr / 0.0015)
            for age, (male_rate, female_rate) in engine.DEFAULT_MORTALITY_TABLE.items()
        }
        
        engine.fertility_table = scaled_fertility_table
        engine.mortality_table = scaled_mortality_table
        engine.fertility_rate = 1.0
        engine.mortality_multiplier = 1.0
        engine.household_split_probability = 0.001
        
        engine._create_synthetic_population(50000)
        initial_pop = len(engine.citizens)
        
        engine.run(months=600)
        final_pop = len(engine.citizens)
        
        score = (final_pop - initial_pop) / initial_pop * 100
        elapsed = time.time() - combo_start
        
        result = {
            'combo': combo_num,
            'birth_rate': br,
            'mortality_rate': mr,
            'initial_population': initial_pop,
            'final_population': final_pop,
            'score': score,
            'elapsed_seconds': elapsed
        }
        results.append(result)
        
        print(f"   ✅ Pop: {initial_pop} → {final_pop} | Score: {score:+7.2f}% | Time: {elapsed:.1f}s")
        
    except Exception as e:
        print(f"   ❌ ERROR: {e}")

# Sort by combo number and save
results_sorted = sorted(results, key=lambda x: x['combo'])

with open('gridsearch_results_full_50k_50y.json', 'w') as f:
    json.dump(results_sorted, f, indent=2)

print(f"\n✅ All {len(results_sorted)}/25 results saved to gridsearch_results_full_50k_50y.json")

# Summary
if results_sorted:
    scores = [r['score'] for r in results_sorted]
    print(f"""
📊 PODSUMOWANIE:
Min: {min(scores):.2f}%
Max: {max(scores):.2f}%
Mean: {sum(scores)/len(scores):.2f}%
""")
