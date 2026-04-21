"""
Generuj wyniki dla 50k agentów, 50 lat - wszystkie kombinacje parametrów
Wersja 2: Ulepszone monitorowanie i obsługa błędów
"""
import json
import time
import sys
from simulation_engine import SimulationEngine
from disease_model import DiseaseModel
import numpy as np

# Parametry do testowania
birth_rates = [0.01, 0.0225, 0.035, 0.0475, 0.06]
mortality_rates = [0.0005, 0.001125, 0.00175, 0.002375, 0.003]

results_full = []
start_time = time.time()
total_combos = len(birth_rates) * len(mortality_rates)

print("="*80, flush=True)
print("SYMULACJA PEŁNA: 50,000 AGENTÓW, 50 LAT", flush=True)
print("="*80, flush=True)
print(f"\nRazem kombinacji: {total_combos}", flush=True)
print(f"Szacunkowy czas: 50-75 minut\n", flush=True)

log_file = open('simulation_progress.log', 'w', buffering=1)

combo_num = 0
for birth_rate in birth_rates:
    for mortality_rate in mortality_rates:
        combo_num += 1
        combo_start = time.time()
        
        try:
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
            print(f"[{combo_num:2d}/{total_combos}] BR={birth_rate:.4f}, MR={mortality_rate:.6f} - Starting...", flush=True)
            sys.stdout.flush()
            
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
            
            progress_msg = (
                f"[{combo_num:2d}/{total_combos}] BR={birth_rate:.4f}, MR={mortality_rate:.6f} | " + 
                f"Pop: {initial_pop:6d} → {final_pop:6d} | " +
                f"Score: {score:+7.2f}% | " +
                f"Time: {elapsed:5.1f}s | " +
                f"ETA: {estimated_remaining/60:6.1f}min"
            )
            
            print(progress_msg, flush=True)
            log_file.write(progress_msg + "\n")
            log_file.flush()
            
        except Exception as e:
            error_msg = f"[{combo_num:2d}/{total_combos}] ERROR - BR={birth_rate:.4f}, MR={mortality_rate:.6f}: {str(e)}"
            print(error_msg, flush=True)
            log_file.write(error_msg + "\n")
            log_file.flush()
            continue

# Zapisz wyniki
output_file = f'gridsearch_results_full_50k_50y.json'
with open(output_file, 'w') as f:
    json.dump(results_full, f, indent=2)

log_file.write("\n" + "="*80 + "\n")
log_file.write(f"✅ Wyniki zapisane: {output_file}\n")
log_file.write(f"Całkowity czas: {(time.time() - start_time)/60:.1f} minut\n")
log_file.write("="*80 + "\n")

print("\n" + "="*80, flush=True)
print(f"✅ Wyniki zapisane: {output_file}", flush=True)
print(f"Całkowity czas: {(time.time() - start_time)/60:.1f} minut", flush=True)
print("="*80, flush=True)

# Podsumowanie
if results_full:
    print(f"""
📊 PODSUMOWANIE WYNIKÓW (50K AGENTÓW, 50 LAT):

Min score: {min(r['score'] for r in results_full):.2f}%
Max score: {max(r['score'] for r in results_full):.2f}%
Średni score: {np.mean([r['score'] for r in results_full]):.2f}%
Mediana: {np.median([r['score'] for r in results_full]):.2f}%

🏆 TOP 5 konfiguracji:
""", flush=True)
    
    for i, r in enumerate(sorted(results_full, key=lambda x: -x['score'])[:5]):
        msg = (f"  {i+1}. BR={r['birth_rate']:.4f}, MR={r['mortality_rate']:.6f} → {r['score']:+7.2f}% " +
               f"(Pop: {r['initial_population']} → {r['final_population']})")
        print(msg, flush=True)
        log_file.write(msg + "\n")

log_file.close()
print(f"\n📋 Logs saved to: simulation_progress.log", flush=True)
