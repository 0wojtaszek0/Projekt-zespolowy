"""
Generuj wyniki dla 50k agentów, 50 lat - wszystkie kombinacje parametrów
"""
import json
import time
from simulation_engine import SimulationEngine
from disease_model import DiseaseModel
import numpy as np

# Parametry do testowania
birth_rates = [0.01, 0.0225, 0.035, 0.0475, 0.06]
mortality_rates = [0.0005, 0.001125, 0.00175, 0.002375, 0.003]

results_full = []
start_time = time.time()
total_combos = len(birth_rates) * len(mortality_rates)

print("="*80)
print("SYMULACJA PEŁNA: 50,000 AGENTÓW, 50 LAT")
print("="*80)
print(f"\nRazem kombinacji: {total_combos}")
print(f"Szacunkowy czas: 50-75 minut\n")

combo_num = 0
for birth_rate in birth_rates:
    for mortality_rate in mortality_rates:
        combo_num += 1
        combo_start = time.time()
        
        # Inicjalizacja
        disease_model = DiseaseModel()
        engine = SimulationEngine(disease_model=disease_model, seed=42)
        
        # Skalowanie parametrów V2
        scaled_fertility_table = {
            age: rate * birth_rate / 0.03
            for age, rate in engine.DEFAULT_FERTILITY_TABLE.items()
        }
        
        scaled_mortality_table = {
            age: (male_rate * mortality_rate / 0.0015, female_rate * mortality_rate / 0.0015)
            for age, (male_rate, female_rate) in engine.DEFAULT_MORTALITY_TABLE.items()
        }
        
        engine.fertility_table = scaled_fertility_table
        engine.mortality_table = scaled_mortality_table
        engine.fertility_rate = 1.0
        engine.mortality_multiplier = 1.0
        engine.household_split_probability = 0.001
        
        # Populacja syntetyczna
        engine._create_synthetic_population(50000)
        initial_pop = len(engine.citizens)
        
        # Symulacja 50 lat
        engine.run(months=600)
        final_pop = len(engine.citizens)
        
        # Score: % zmiana
        score = (final_pop - initial_pop) / initial_pop * 100
        
        # Czas
        elapsed = time.time() - combo_start
        
        # Rezultat
        result = {
            'combo': combo_num,
            'birth_rate': birth_rate,
            'mortality_rate': mortality_rate,
            'initial_population': initial_pop,
            'final_population': final_pop,
            'score': score,
            'elapsed_seconds': elapsed
        }
        results_full.append(result)
        
        # Progress
        total_elapsed = time.time() - start_time
        avg_time = total_elapsed / combo_num
        estimated_remaining = (total_combos - combo_num) * avg_time
        
        print(f"[{combo_num:2d}/{total_combos}] BR={birth_rate:.4f}, MR={mortality_rate:.6f} | " + 
              f"Pop: {initial_pop:6d} → {final_pop:6d} | " +
              f"Score: {score:+7.2f}% | " +
              f"Time: {elapsed:5.1f}s | " +
              f"ETA: {estimated_remaining/60:6.1f}min")

# Zapisz wyniki
output_file = f'gridsearch_results_full_50k_50y.json'
with open(output_file, 'w') as f:
    json.dump(results_full, f, indent=2)

print("\n" + "="*80)
print(f"✅ Wyniki zapisane: {output_file}")
print(f"Całkowity czas: {(time.time() - start_time)/60:.1f} minut")
print("="*80)

# Podsumowanie
print(f"""
📊 PODSUMOWANIE WYNIKÓW (50K AGENTÓW, 50 LAT):

Min score: {min(r['score'] for r in results_full):.2f}%
Max score: {max(r['score'] for r in results_full):.2f}%
Średni score: {np.mean([r['score'] for r in results_full]):.2f}%

🏆 TOP 5 konfiguracji:
""")

for i, r in enumerate(sorted(results_full, key=lambda x: -x['score'])[:5]):
    print(f"  {i+1}. BR={r['birth_rate']:.4f}, MR={r['mortality_rate']:.6f} → {r['score']:+7.2f}% " +
          f"(Pop: {r['initial_population']} → {r['final_population']})")

