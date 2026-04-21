import numpy as np
from itertools import product
from simulation_engine import SimulationEngine
from disease_model import DiseaseModel
import json
from datetime import datetime


class GridSearchOptimization:
    """
    Grid Search Optimization dla 2 parametrów demograficznych.
    Parametry: fertility_multiplier i mortality_multiplier
    """
    
    def __init__(self, param_grid, scoring_function, n_iter=1, verbose=True):
        """
        Args:
            param_grid: Dict z parametrami do optymalizacji
                        {"fertility_multiplier": [...], "mortality_multiplier": [...]}
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
        self.best_score = -float('inf')

    def optimize(self):
        """
        Przeprowadź grid search dla 2 parametrów.
        """
        param_names = list(self.param_grid.keys())
        param_values = list(self.param_grid.values())
        
        total_combinations = np.prod([len(v) for v in param_values])
        
        if self.verbose:
            print("\n" + "="*60)
            print(f"GRID SEARCH OPTIMIZATION - {len(param_names)} PARAMETRY")
            print("="*60)
            print(f"Parametry: {param_names}")
            print(f"Wartości param 1: {param_values[0]}")
            print(f"Wartości param 2: {param_values[1]}")
            print(f"Razem kombinacji: {total_combinations}")
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
                    
                    if score > self.best_score:
                        self.best_score = score
                        self.best_params = params
                    
                    if self.verbose:
                        fert = params[param_names[0]]
                        mort = params[param_names[1]]
                        print(f"[{current_combo:4d}/{total_combinations}] "
                              f"{param_names[0]}: {fert:6.3f} | "
                              f"{param_names[1]}: {mort:6.3f} | "
                              f"Score: {score:10.4f}")
                
                except Exception as e:
                    print(f"BŁĄD w kombinacji {params}: {e}")
                    self.results.append({
                        "combo": current_combo,
                        "iteration": iteration + 1,
                        "params": params,
                        "score": -1000,
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
        """Zwróć wyniki w formie numpy array dla analizy"""
        if not self.results:
            return None
        
        results_sorted = sorted(self.results, key=lambda x: x["score"], reverse=True)
        return results_sorted
    
    def save_results(self, filename="gridsearch_results.json"):
        """Zapisz wyniki do JSON"""
        # Konwertuj numpy wartości na float
        results_serializable = []
        for r in self.results:
            r_copy = r.copy()
            r_copy["params"] = {k: float(v) if isinstance(v, np.ndarray) else v 
                               for k, v in r_copy["params"].items()}
            r_copy["score"] = float(r_copy["score"])
            results_serializable.append(r_copy)
        
        with open(filename, 'w') as f:
            json.dump(results_serializable, f, indent=2)
        
        if self.verbose:
            print(f"Zapisano wyniki do: {filename}")

# PRZYKŁAD UŻYCIA
if __name__ == "__main__":
    def simulation_scoring_function(fertility_multiplier, mortality_multiplier):
        """
        Funkcja ewaluacyjna dla 2 parametrów demograficznych.
        
        Args:
            fertility_multiplier: Mnożnik współczynnika płodności
            mortality_multiplier: Mnożnik współczynnika śmiertelności
            
        Returns:
            score: Zmiana populacji (%) - im wyższa, tym lepiej
        """
        try:
            # Inicjalizacja modelu choroby
            disease_model = DiseaseModel()
            
            # Stwórz silnik symulacji z danymi parametrami
            engine = SimulationEngine(disease_model=disease_model, seed=42)
            
            # Ustaw mnożniki demograficzne
            engine.fertility_rate = fertility_multiplier
            engine.mortality_multiplier = mortality_multiplier
            engine.household_split_probability = 0.001
            
            # Wygeneruj małą populację syntetyczną (szybciej)
            population_size = 1000
            engine._create_synthetic_population(population_size)
            
            # Uruchom symulację na 10 lat
            engine.run(months=120)
            
            # Oblicz score: zmianę populacji
            final_pop = len([c for c in engine.citizens.values() if c.alive])
            score = ((final_pop - population_size) / population_size) * 100
            
            return score
            
        except Exception as e:
            print(f"Błąd w symulacji: {e}")
            return -1000  # Kara za błędy

    # Parametry do optymalizacji - TYLKO 2 PARAMETRY!
    param_grid = {
        "fertility_multiplier": np.linspace(0.5, 2.0, 5),   # 5 wartości
        "mortality_multiplier": np.linspace(0.5, 2.0, 5),   # 5 wartości
    }
    # Razem: 5 x 5 = 25 kombinacji

    print("\nGRIDSEARCH KONFIGURACJA (2 PARAMETRY):")
    print(f"  Fertility multiplier: {[f'{x:.3f}' for x in param_grid['fertility_multiplier']]}")
    print(f"  Mortality multiplier: {[f'{x:.3f}' for x in param_grid['mortality_multiplier']]}")
    print(f"  Razem kombinacji: {np.prod([len(v) for v in param_grid.values()])}\n")
    
    # Uruchom grid search
    optimizer = GridSearchOptimization(
        param_grid=param_grid,
        scoring_function=simulation_scoring_function,
        n_iter=1,  # Liczba powtórzeń
        verbose=True
    )
    
    best_params, best_score = optimizer.optimize()
    
    # Zapisz wyniki
    optimizer.save_results(f"gridsearch_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    
    # Wypisz Top 5 wyników
    print("\nTOP 5 WYNIKÓW:")
    print("-" * 60)
    results = optimizer.get_results_dataframe()
    for i, result in enumerate(results[:5], 1):
        params = result["params"]
        score = result["score"]
        print(f"{i}. Fertility: {params['fertility_multiplier']:.3f} | "
              f"Mortality: {params['mortality_multiplier']:.3f} | "
              f"Score: {score:.4f}")