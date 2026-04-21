"""
Symulacja z optymalnymi parametrami z grid search'a
BR=0.06 (birth rate), MR=0.001125 (mortality rate)
50,000 agentów, 50 lat
"""
from simulation_engine import SimulationEngine
from disease_model import DiseaseModel
from visualization import SimulationVisualizer
import json

print("="*80)
print("SYMULACJA Z OPTYMALNYMI PARAMETRAMI")
print("="*80)
print("""
Parametry z Grid Search (50k agents, 50 years):
  Birth Rate: 0.06
  Mortality Rate: 0.001125
  
Oczekiwany wynik: +45.48% wzrostu populacji
""")

# Optymalne parametry
optimal_birth_rate = 0.06
optimal_mortality_rate = 0.001125

# Inicjalizacja
disease_model = DiseaseModel()
engine = SimulationEngine(disease_model=disease_model, seed=42)

# Skalowanie tabeli płodności
scaled_fertility_table = {
    age: rate * optimal_birth_rate / 0.03
    for age, rate in engine.DEFAULT_FERTILITY_TABLE.items()
}

# Skalowanie tabeli śmiertelności
scaled_mortality_table = {
    age: (male_rate * optimal_mortality_rate / 0.0015, 
           female_rate * optimal_mortality_rate / 0.0015)
    for age, (male_rate, female_rate) in engine.DEFAULT_MORTALITY_TABLE.items()
}

# Ustaw parametry
engine.fertility_table = scaled_fertility_table
engine.mortality_table = scaled_mortality_table
engine.fertility_rate = 1.0
engine.mortality_multiplier = 1.0
engine.household_split_probability = 0.001

# Wygeneruj populację
print("\n📊 Generowanie populacji syntetycznej (50,000 obywateli)...")
engine._create_synthetic_population(50000)
initial_pop = len(engine.citizens)
print(f"   ✅ Utworzono: {initial_pop} obywateli w {len(engine.households)} gospodarstwach")

# Uruchom symulację
print("\n🔄 Uruchamianie symulacji na 50 lat (600 miesięcy)...")
engine.run(months=600)

final_pop = len(engine.citizens)
score = (final_pop - initial_pop) / initial_pop * 100

print("\n" + "="*80)
print("WYNIKI")
print("="*80)
print(f"""
Populacja początkowa: {initial_pop:,}
Populacja końcowa:    {final_pop:,}
Wzrost populacji:     {final_pop - initial_pop:,} osób
Zmiana procentowa:    {score:+.2f}%

Gospodarstwach:       {len(engine.households)}
Strefy:               {len(engine.zones)}
""")

# Wygeneruj piramidy wieku
print("\n📈 Generowanie piramid wieku...")
visualizer = SimulationVisualizer(engine.yearly_stats)

# Piramida wieku
visualizer.plot_interactive_age_pyramid()
print("   ✅ age_pyramid_interactive.html")

# Wszystkie wykresy
visualizer.generate_all_plots()
print("   ✅ All plots generated")

# Zapisz wyniki do JSON
results = {
    'simulation': 'optimal_parameters',
    'birth_rate': optimal_birth_rate,
    'mortality_rate': optimal_mortality_rate,
    'duration_years': 50,
    'duration_months': 600,
    'initial_population': initial_pop,
    'final_population': final_pop,
    'population_change': final_pop - initial_pop,
    'population_change_percent': score,
    'households': len(engine.households),
    'zones': len(engine.zones)
}

with open('optimal_simulation_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print("   ✅ optimal_simulation_results.json")

print("\n" + "="*80)
print("✅ SYMULACJA UKOŃCZONA POMYŚLNIE")
print("="*80)
