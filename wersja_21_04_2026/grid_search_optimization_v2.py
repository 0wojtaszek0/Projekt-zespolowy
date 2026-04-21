"""
Grid Search Optimization V2 - 2 parametry: birth_rate i mortality_rate
Optymalizacja bezwzględnych współczynników demograficznych (zamiast multiplierów)
"""

import numpy as np
from itertools import product
from simulation_engine import SimulationEngine
from disease_model import DiseaseModel
import json
from datetime import datetime


class GridSearchOptimizationV2:
    """
    Grid Search Optimization dla 2 parametrów demograficznych: birth_rate i mortality_rate.
    Bez multiplierów - bezpośrednie optymalizowanie współczynników.
    """
    
    def __init__(self, param_grid, scoring_function, n_iter=1, verbose=True):
        """
        Args:
            param_grid: Dict z parametrami do optymalizacji
                        {"birth_rate": [...], "mortality_rate": [...]}
            scoring_function: Funkcja ewaluacyjna
            n_iter: Liczba iteracji (dla powtórzeń)
            verbose: Drukuj informacje o postępie
        """
        self.param_grid = param_grid
        self.scoring_function = scoring_function
        self.n_iter = n_iter
        self.verbose = verbose
        self.results = []
        self.best_params = None
        self.best_score = float('inf')

    def optimize(self):
        """
        Przeprowadź grid search dla 2 parametrów (birth_rate, mortality_rate).
        """
        param_names = list(self.param_grid.keys())
        param_values = list(self.param_grid.values())
        
        total_combinations = np.prod([len(v) for v in param_values])
        
        if self.verbose:
            print("\n" + "="*60)
            print("GRID SEARCH OPTIMIZATION V2 - 2 PARAMETRY (RATES)")
            print("="*60)
            print(f"Parametry: {param_names}")
            print(f"Wartości param 1: {[f'{x:.5f}' for x in param_values[0]]}")
            print(f"Wartości param 2: {[f'{x:.5f}' for x in param_values[1]]}")
            print(f"Razem kombinacji: {int(total_combinations)}")
            print("="*60 + "\n")
        
        current_combo = 0
        
        for iteration in range(self.n_iter):
            if self.verbose and self.n_iter > 1:
                print(f"\n--- ITERACJA {iteration + 1}/{self.n_iter} ---\n")
            
            for values in product(*param_values):
                current_combo += 1
                params = dict(zip(param_names, values))
                
                try:
                    score = self.scoring_function(**params)
                    
                    result = {
                        "combo": current_combo,
                        "iteration": iteration + 1,
                        "params": params,
                        "score": score
                    }
                    self.results.append(result)
                    
                    if score < self.best_score:
                        self.best_score = score
                        self.best_params = params
                    
                    if self.verbose:
                        birth = params[param_names[0]]
                        mort = params[param_names[1]]
                        print(f"[{current_combo:4d}/{int(total_combinations)}] "
                              f"birth_rate: {birth:.5f} | "
                              f"mortality_rate: {mort:.5f} | "
                              f"Score: {score:10.4f}")
                
                except Exception as e:
                    print(f"BŁĄD w kombinacji {params}: {e}")
                    self.results.append({
                        "combo": current_combo,
                        "iteration": iteration + 1,
                        "params": params,
                        "score": 1000,
                        "error": str(e)
                    })
        
        if self.verbose:
            print("\n" + "="*60)
            print("RESULTAT KOŃCOWY")
            print("="*60)
            print(f"Najlepsze parametry: {self.best_params}")
            print(f"Najlepszy score: {self.best_score:.4f}")
            print("="*60 + "\n")
        
        return self.best_params, self.best_score
    
    def get_results_dataframe(self):
        """Zwróć wyniki w formie listy dla analizy"""
        if not self.results:
            return None
        
        results_sorted = sorted(self.results, key=lambda x: x["score"], reverse=False)
        return results_sorted
    
    def save_results(self, filename="gridsearch_results_v2.json"):
        """Zapisz wyniki do JSON"""
        results_serializable = []
        for r in self.results:
            r_copy = r.copy()
            r_copy["params"] = {k: float(v) if isinstance(v, (np.ndarray, np.floating)) else v 
                               for k, v in r_copy["params"].items()}
            r_copy["score"] = float(r_copy["score"])
            results_serializable.append(r_copy)
        
        with open(filename, 'w') as f:
            json.dump(results_serializable, f, indent=2)
        
        if self.verbose:
            print(f"Zapisano wyniki do: {filename}")


# PRZYKŁAD UŻYCIA
if __name__ == "__main__":
    def simulation_scoring_function_v2(birth_rate, mortality_rate):
        """
        Funkcja ewaluacyjna dla 2 parametrów demograficznych (rates).
        
        Args:
            birth_rate: Współczynnik narodzin (bezwzględny)
            mortality_rate: Współczynnik śmiertelności (bezwzględny)
            
        Returns:
            score: Zmiana populacji (%) - im wyższa, tym lepiej
        """
        try:
            # Inicjalizacja modelu choroby
            disease_model = DiseaseModel()
            
            # Stwórz silnik symulacji z danymi parametrami
            engine = SimulationEngine(disease_model=disease_model, seed=42)
            
            # WAŻNE: Skala domyślnych tabel fertility i mortality
            # Skalowanie tabeli płodności
            scaled_fertility_table = {
                age: rate * birth_rate / 0.03  # Skaluj względem domyślnego birth rate
                for age, rate in engine.DEFAULT_FERTILITY_TABLE.items()
            }
            
            # Skalowanie tabeli śmiertelności
            scaled_mortality_table = {
                age: (male_rate * mortality_rate / 0.0015, female_rate * mortality_rate / 0.0015)
                for age, (male_rate, female_rate) in engine.DEFAULT_MORTALITY_TABLE.items()
            }
            
            # Ustaw przeskalowane tabele
            engine.fertility_table = scaled_fertility_table
            engine.mortality_table = scaled_mortality_table
            
            # Ustaw multiplery na 1.0 (bez dodatkowych modyfikacji)
            engine.fertility_rate = 1.0
            engine.mortality_multiplier = 1.0
            engine.household_split_probability = 0.001
            
            # Wygeneruj małą populację syntetyczną (szybciej)
            population_size = 1000
            engine._create_synthetic_population(population_size)
            
            # Uruchom symulację na 10 lat
            engine.run(months=120)
            
            # Oblicz score: zmianę populacji
            final_pop = len([c for c in engine.citizens.values() if c.alive])
            score = abs(((final_pop - population_size) / population_size) * 100)
            
            return score
            
        except Exception as e:
            print(f"Błąd w symulacji: {e}")
            return 1000  # Kara za błędy

    # Parametry do optymalizacji - RATES (bezwzględne współczynniki)
    param_grid = {
        "birth_rate": np.linspace(0.005, 0.08, 10),       # 10 wartości (od 0.005 do 0.08)
        "mortality_rate": np.linspace(0.0005, 0.003, 10), # 10 wartości
    }
    # Razem: 10 x 10 = 100 kombinacji

    print("\nGRIDSEARCH KONFIGURACJA V2 (BIRTH_RATE & MORTALITY_RATE):")
    print(f"  Birth rate: {[f'{x:.5f}' for x in param_grid['birth_rate']]}")
    print(f"  Mortality rate: {[f'{x:.5f}' for x in param_grid['mortality_rate']]}")
    print(f"  Razem kombinacji: {np.prod([len(v) for v in param_grid.values()])}\n")
    
    # Uruchom grid search
    optimizer = GridSearchOptimizationV2(
        param_grid=param_grid,
        scoring_function=simulation_scoring_function_v2,
        n_iter=1,
        verbose=True
    )
    
    best_params, best_score = optimizer.optimize()
    
    # Zapisz wyniki
    optimizer.save_results(f"gridsearch_results_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    
    # Wypisz Top 5 wyników
    print("\nTOP 5 WYNIKÓW:")
    print("-" * 70)
    results = optimizer.get_results_dataframe()
    for i, result in enumerate(results[:5], 1):
        params = result["params"]
        score = result["score"]
        print(f"{i}. Birth rate: {params['birth_rate']:.5f} | "
              f"Mortality rate: {params['mortality_rate']:.5f} | "
              f"Score: {score:.4f}")
