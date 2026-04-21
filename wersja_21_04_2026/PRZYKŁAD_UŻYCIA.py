"""
QUICK START GUIDE - Nowe Narzędzia Gridsearch V3
=================================================

Ten plik zawiera gotowe przykłady do szybkiego przystania korzystania
z ulepszonych narzędzi gridsearch, profiling i analiza pamięci.
"""

# ==============================================================================
# PRZYKŁAD 1: Szybki Gridsearch V3 (10×10 parametrów)
# ==============================================================================
"""
Uruchomienie:
  python -c "
from grid_search_improved_v3 import GridSearchImprovedV3
import numpy as np

def scoring(fertility_multiplier, mortality_multiplier):
    # Szybki scoring na małej populacji
    population = 50000
    for year in range(50):
        births = population * 0.03 * fertility_multiplier
        deaths = population * 0.0015 * mortality_multiplier
        population += births - deaths
        if population < 0:
            population = 0
            break
    annual_growth = (population - 50000) / 50000 / 50 * 100
    return abs(annual_growth)

param_grid = {
    'fertility_multiplier': np.linspace(0.1, 2.8, 10),
    'mortality_multiplier': np.linspace(0.1, 2.8, 10),
}

optimizer = GridSearchImprovedV3(param_grid, scoring, verbose=True)
best_params, best_score = optimizer.optimize()
optimizer.check_optimum_not_at_edge()
optimizer.create_heatmap_with_functions()
"
"""

# ==============================================================================
# PRZYKŁAD 2: Profiling Wydajności Symulacji
# ==============================================================================
"""
Plik: performance_profiling_example.py
"""

from performance_profiler import PerformanceProfiler, MemoryAnalyzer
from simulation_engine import SimulationEngine
from disease_model import DiseaseModel
import time


def profile_example():
    """Przykład kompletnego profilingu wydajności."""
    
    print("="*80)
    print("PERFORMANCE PROFILING EXAMPLE")
    print("="*80)
    
    # 1. Inicjalizuj engine
    print("\n1. Initializing simulation engine...")
    disease_model = DiseaseModel()
    engine = SimulationEngine(disease_model=disease_model, seed=42)
    
    # 2. Stwórz populację
    print("2. Creating synthetic population (5000 agents)...")
    engine._create_synthetic_population(5000)
    
    # 3. Sprawdź pamięć PRZED
    print("\n3. Memory BEFORE simulation:")
    print(MemoryAnalyzer.report_memory_usage(engine))
    
    # 4. Profile kroków symulacji
    print("\n4. Profiling simulation steps...")
    profiler = PerformanceProfiler()
    step_times = profiler.profile_simulation_step(engine, num_steps=20)
    
    # 5. Sprawdź pamięć PO
    print("\n5. Memory AFTER simulation:")
    print(MemoryAnalyzer.report_memory_usage(engine))
    
    # 6. Analiza struktur
    print("\n6. Data structures analysis:")
    print(MemoryAnalyzer.analyze_data_structures(engine))
    
    # 7. Podsumowanie
    print("\n7. Summary:")
    print(profiler.get_summary())


# ==============================================================================
# PRZYKŁAD 3: Gridsearch + Profiling
# ==============================================================================
"""
Plik: gridsearch_with_profiling_example.py
"""

def gridsearch_with_profiling_example():
    """Kombinacja gridsearch z analizą wydajności."""
    
    from grid_search_improved_v3 import GridSearchImprovedV3
    import numpy as np
    import time
    
    def scoring_with_profiling(fertility_multiplier, mortality_multiplier):
        """Scoring function z wbudowanym profilingu."""
        
        start = time.perf_counter()
        
        # Szybka symulacja
        population = 50000
        for year in range(50):
            births = population * 0.03 * fertility_multiplier
            deaths = population * 0.0015 * mortality_multiplier
            population += births - deaths
            if population < 0:
                population = 0
                break
        
        annual_growth = (population - 50000) / 50000 / 50 * 100
        elapsed = time.perf_counter() - start
        
        print(f"    [f={fertility_multiplier:.2f}, m={mortality_multiplier:.2f}] "
              f"score={abs(annual_growth):.2f} [{elapsed:.2f}s]")
        
        return abs(annual_growth)
    
    # Gridsearch
    param_grid = {
        'fertility_multiplier': np.linspace(0.5, 2.1, 5),
        'mortality_multiplier': np.linspace(0.5, 2.1, 5),
    }
    
    print("\nRunning GridSearch with profiling...\n")
    
    optimizer = GridSearchImprovedV3(param_grid, scoring_with_profiling, verbose=True)
    best_params, best_score = optimizer.optimize()
    
    print("\nOptimum found:")
    print(f"  Parameters: {best_params}")
    print(f"  Score: {best_score:.2f}")
    
    optimizer.check_optimum_not_at_edge()
    optimizer.create_heatmap_with_functions('example_heatmap.png')
    optimizer.save_results('example_results.json')


# ==============================================================================
# PRZYKŁAD 4: Analiza Struktury Danych Agentów
# ==============================================================================
"""
Plik: analyze_structure_example.py
"""

def analyze_agent_structure():
    """Analiza struktury przechowywania agentów."""
    
    from performance_profiler import print_structure_info, MemoryAnalyzer
    from simulation_engine import SimulationEngine
    from disease_model import DiseaseModel
    
    # Wypisz informacje o strukturze
    print_structure_info()
    
    # Utwórz engine i populację
    disease_model = DiseaseModel()
    engine = SimulationEngine(disease_model=disease_model, seed=42)
    engine._create_synthetic_population(10000)
    
    # Analiza
    print("\nDetailed analysis for 10,000 agents:")
    usage = MemoryAnalyzer.get_agent_memory_usage(engine)
    
    for key, value in usage.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value:,}")


# ==============================================================================
# PRZYKŁAD 5: Pełna Skala (dla cierpliwych!)
# ==============================================================================
"""
Plik: fullscale_gridsearch_example.py

UWAGA: To będzie trwać ~8-16 godzin!
"""

def fullscale_example():
    """Pełna skala gridsearch (50k agentów, 50 lat)."""
    
    from gridsearch_fullscale import FullScaleGridSearch, full_scale_scoring
    import numpy as np
    
    print("\n" + "="*80)
    print("FULL-SCALE GRID SEARCH EXAMPLE")
    print("="*80)
    
    print("\nWARNING: This will take ~8-16 hours!")
    print("Alternatywnie, zmień parametry na mniejszy grid (5x5 zamiast 10x10)")
    
    # Zmniejsz na test (3x3 zamiast 10x10)
    param_grid = {
        'fertility_multiplier': np.linspace(0.5, 2.1, 3),  # 3 zamiast 10
        'mortality_multiplier': np.linspace(0.5, 2.1, 3),  # 3 zamiast 10
    }
    
    print(f"\nUsing 3x3 grid for faster testing ({3*3} combinations)")
    
    optimizer = FullScaleGridSearch(
        param_grid=param_grid,
        scoring_function=full_scale_scoring,
        verbose=True
    )
    
    best_params, best_score = optimizer.optimize()
    optimizer.check_optimum_not_at_edge()
    optimizer.create_heatmap('fullscale_test_heatmap.png')
    optimizer.save_results('fullscale_test_results.json')


# ==============================================================================
# PRZYKŁAD 6: Szybki Test
# ==============================================================================
"""
Najszybszy test - zamiast pełnych 50 lat, użyj 1-2 lat
"""

def quick_test():
    """Szybki test wydajności bez czekania."""
    
    from grid_search_improved_v3 import GridSearchImprovedV3
    import numpy as np
    
    def quick_scoring(fertility_multiplier, mortality_multiplier):
        """Bardzo szybka ocena (tylko 1 rok)."""
        population = 50000
        
        # Tylko 1 rok zamiast 50
        births = population * 0.03 * fertility_multiplier
        deaths = population * 0.0015 * mortality_multiplier
        population += births - deaths
        
        annual_growth = (population - 50000) / 50000 * 100
        return abs(annual_growth)
    
    # Mały grid
    param_grid = {
        'fertility_multiplier': np.linspace(0.5, 2.1, 5),
        'mortality_multiplier': np.linspace(0.5, 2.1, 5),
    }
    
    print("\nQuick test (5x5 grid, 1-year sim per combo)...")
    
    optimizer = GridSearchImprovedV3(param_grid, quick_scoring, verbose=True)
    best_params, best_score = optimizer.optimize()
    
    print("\nResults:")
    print(f"  Best parameters: {best_params}")
    print(f"  Best score: {best_score:.2f}")
    
    optimizer.check_optimum_not_at_edge()
    optimizer.create_heatmap_with_functions('quick_test_heatmap.png')


# ==============================================================================
# MAIN: Uruchom przykłady
# ==============================================================================

if __name__ == "__main__":
    
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║         QUICK START GUIDE - GRID SEARCH V3 EXAMPLES                        ║
╚════════════════════════════════════════════════════════════════════════════╝

Dostępne przykłady:

1. quick_test()
   - Szybki test (5x5 grid, 1 rok na kombinację)
   - Czas: ~1-2 minuty
   - Wynik: heatmapa PNG

2. profile_example()
   - Profiling wydajności i pamięci
   - 5000 agentów, 20 kroków
   - Czas: ~5 minut
   - Wynik: szczegółowy raport

3. gridsearch_with_profiling_example()
   - Gridsearch + wbudowany profiling
   - 25 kombinacji
   - Czas: ~2-3 minuty
   - Wynik: heatmapa, JSON z wynikami

4. analyze_agent_structure()
   - Analiza struktury przechowywania agentów
   - Informacje o pamięci
   - Rekomendacje optymalizacji

5. fullscale_example()
   - Pełna skala (50k agentów, 50 lat)
   - ⚠️  Trwa ~8-16 godzin!
   - Redaktor: zmniejszona do 3x3 dla testu

Uruchomienie:
python -c "from PRZYKŁAD_UŻYCIA import *; quick_test()"

Albo importuj w swoim skrypcie:
from PRZYKŁAD_UŻYCIA import quick_test, profile_example
quick_test()
""")
    
    # Uruchom szybki test
    print("\nRunning quick_test()...\n")
    quick_test()
