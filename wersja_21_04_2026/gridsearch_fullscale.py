"""
Full-Scale Grid Search with Heatmap (50,000 agents, 50 years)

Stwórz mapę ciepła dla pełnej skali symulacji z ulepszoną wizualizacją.
- Rozszerzone zakresy parametrów (10x10)
- Mapa ciepła w matplotlib z kolorami 'bwr'
- Rysowanie funkcji wpływu poszczególnych parametrów
- Równomierne podziały etykiet
- Sprawdzenie czy optimum nie na krawędzi
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import Normalize
import json
from datetime import datetime
from itertools import product
import time

from simulation_engine import SimulationEngine
from disease_model import DiseaseModel
from performance_profiler import MemoryAnalyzer, PerformanceProfiler


class FullScaleGridSearch:
    """
    Grid Search dla pełnej skali: 50,000 agentów, 50 lat.
    Optymalizacja z lepszą wizualizacją i analizą.
    """
    
    def __init__(self, param_grid, scoring_function, verbose=True):
        self.param_grid = param_grid
        self.scoring_function = scoring_function
        self.verbose = verbose
        self.results = []
        self.best_params = None
        self.best_score = float('inf')
        self.lowest_score = float('inf')
        self.highest_score = -float('inf')
        self.execution_times = []
    
    def optimize(self):
        """Wykonaj full-scale grid search."""
        param_names = list(self.param_grid.keys())
        param_values = list(self.param_grid.values())
        
        total_combinations = int(np.prod([len(v) for v in param_values]))
        
        if self.verbose:
            print("\n" + "="*80)
            print("FULL-SCALE GRID SEARCH OPTIMIZATION")
            print("="*80)
            print(f"Simulation Parameters:")
            print(f"  - Population size: 50,000 agents")
            print(f"  - Duration: 50 years (600 months)")
            print(f"  - Disease model: Integrated")
            print(f"\nOptimization Parameters:")
            print(f"  - Param 1 ({param_names[0]}): {[f'{x:.3f}' for x in param_values[0]]}")
            print(f"  - Param 2 ({param_names[1]}): {[f'{x:.3f}' for x in param_values[1]]}")
            print(f"  - Total combinations: {total_combinations}")
            print(f"  - Objective: Minimize |annual_growth_rate|")
            print("="*80 + "\n")
        
        current_combo = 0
        total_start = time.time()
        
        for values in product(*param_values):
            current_combo += 1
            params = dict(zip(param_names, values))
            
            combo_start = time.time()
            
            try:
                score = self.scoring_function(**params)
                
                combo_time = time.time() - combo_start
                self.execution_times.append(combo_time)
                
                result = {
                    "combo": current_combo,
                    "params": params,
                    "score": score,
                    "execution_time": combo_time
                }
                self.results.append(result)
                
                if score < self.best_score:
                    self.best_score = score
                    self.best_params = params.copy()
                
                self.lowest_score = min(self.lowest_score, score)
                self.highest_score = max(self.highest_score, score)
                
                # Progress output
                elapsed = time.time() - total_start
                avg_time_per_combo = elapsed / current_combo
                remaining_combos = total_combinations - current_combo
                eta_seconds = remaining_combos * avg_time_per_combo
                
                if self.verbose and (current_combo % 5 == 0 or current_combo == 1):
                    param_str = " | ".join([f"{p}: {v:.2f}" for p, v in params.items()])
                    print(f"[{current_combo:2d}/{total_combinations}] {param_str:40} | "
                          f"Score: {score:8.2f} | Time: {combo_time:6.1f}s | "
                          f"ETA: ~{int(eta_seconds//60):3d}min")
            
            except Exception as e:
                print(f"ERROR in combo {current_combo} {params}: {e}")
                self.results.append({
                    "combo": current_combo,
                    "params": params,
                    "score": 10000,
                    "error": str(e)
                })
        
        total_time = time.time() - total_start
        
        if self.verbose:
            print("\n" + "="*80)
            print("OPTIMIZATION COMPLETE")
            print("="*80)
            print(f"Best score (minimum growth rate): {self.best_score:.2f}%")
            print(f"Best parameters: {self.best_params}")
            print(f"Total execution time: {total_time/3600:.2f} hours")
            print(f"Average time per combination: {total_time/total_combinations:.1f}s")
            print("="*80 + "\n")
        
        return self.best_params, self.best_score
    
    def get_results_dataframe(self):
        """Zwróć wyniki jako DataFrame."""
        if not self.results:
            return None
        
        df = pd.DataFrame(self.results)
        params_df = pd.json_normalize(df['params'])
        df = pd.concat([df.drop('params', axis=1), params_df], axis=1)
        return df.sort_values('score')
    
    def save_results(self, filename="gridsearch_fullscale_results.json"):
        """Zapisz wyniki."""
        results_serializable = []
        for r in self.results:
            r_copy = r.copy()
            r_copy["params"] = {k: float(v) if isinstance(v, (np.ndarray, np.floating)) else v 
                               for k, v in r_copy["params"].items()}
            r_copy["score"] = float(r_copy["score"])
            r_copy["execution_time"] = float(r_copy.get("execution_time", 0))
            results_serializable.append(r_copy)
        
        with open(filename, 'w') as f:
            json.dump(results_serializable, f, indent=2)
        
        print(f"✓ Wyniki zapisane do: {filename}")
    
    def create_heatmap(self, output_file='heatmap_fullscale_optimized.png'):
        """Stwórz mapę ciepła w matplotlib."""
        if not self.results:
            print("Brak wyników")
            return
        
        df = self.get_results_dataframe()
        param_names = list(self.param_grid.keys())
        
        x_param = param_names[0]
        y_param = param_names[1]
        
        x_values = sorted(df[x_param].unique())
        y_values = sorted(df[y_param].unique())
        
        # Stwórz macierz
        matrix = np.full((len(y_values), len(x_values)), np.nan)
        
        for i, y_val in enumerate(y_values):
            for j, x_val in enumerate(x_values):
                mask = (df[x_param] == x_val) & (df[y_param] == y_val)
                if mask.any():
                    matrix[i, j] = df[mask]['score'].mean()
        
        # Figurka z subplotami
        fig = plt.figure(figsize=(18, 12))
        
        # GŁÓWNA MAPA CIEPŁA
        ax_main = plt.subplot(2, 2, (1, 2))
        
        norm = Normalize(vmin=self.lowest_score, vmax=self.highest_score)
        im = ax_main.imshow(
            matrix,
            cmap='bwr',
            norm=norm,
            aspect='auto',
            origin='lower',
            extent=[x_values[0], x_values[-1], y_values[0], y_values[-1]],
            interpolation='nearest'
        )
        
        # Etykiety z równomiernym podziałem
        n_x_ticks = 6
        step_x = max(1, len(x_values) // (n_x_ticks - 1))
        x_tick_idx = np.arange(0, len(x_values), step_x)
        ax_main.set_xticks(x_values[x_tick_idx])
        ax_main.set_xticklabels([f'{x_values[i]:.2f}' for i in x_tick_idx], rotation=45, ha='right')
        
        n_y_ticks = 6
        step_y = max(1, len(y_values) // (n_y_ticks - 1))
        y_tick_idx = np.arange(0, len(y_values), step_y)
        ax_main.set_yticks(y_values[y_tick_idx])
        ax_main.set_yticklabels([f'{y_values[i]:.2f}' for i in y_tick_idx])
        
        ax_main.set_xlabel(x_param, fontsize=12, fontweight='bold')
        ax_main.set_ylabel(y_param, fontsize=12, fontweight='bold')
        ax_main.set_title(
            f'Full-Scale Heatmap: 50,000 Agents, 50 Years\n'
            f'Optimization: Minimize |Annual Growth Rate|\n'
            f'(Blue=Better, Red=Worse)',
            fontsize=13, fontweight='bold'
        )
        
        # Kolorbar
        cbar = plt.colorbar(im, ax=ax_main)
        cbar.set_label('Score (|% growth/year|)', rotation=270, labelpad=25)
        
        # Zaznacz optimum
        if self.best_params:
            x_opt = self.best_params[x_param]
            y_opt = self.best_params[y_param]
            ax_main.plot(x_opt, y_opt, 'g*', markersize=25, 
                        label=f'Optimum: {self.best_score:.2f}%',
                        markeredgecolor='darkgreen', markeredgewidth=1.5)
            ax_main.legend(fontsize=11, loc='upper right')
        
        # WPŁYW PARAMETRU 1
        ax_p1 = plt.subplot(2, 2, 3)
        grouped_p1 = df.groupby(x_param)['score'].agg(['mean', 'std']).reset_index()
        grouped_p1 = grouped_p1.sort_values(x_param)
        ax_p1.plot(grouped_p1[x_param], grouped_p1['mean'], 'b-o', linewidth=2, markersize=7)
        ax_p1.fill_between(grouped_p1[x_param],
                          grouped_p1['mean'] - grouped_p1['std'],
                          grouped_p1['mean'] + grouped_p1['std'],
                          alpha=0.3)
        ax_p1.set_xlabel(x_param, fontsize=11, fontweight='bold')
        ax_p1.set_ylabel('Score (|% growth|)', fontsize=11, fontweight='bold')
        ax_p1.set_title(f'Effect of {x_param} on Growth Rate', fontsize=12, fontweight='bold')
        ax_p1.grid(True, alpha=0.3)
        
        # WPŁYW PARAMETRU 2
        ax_p2 = plt.subplot(2, 2, 4)
        grouped_p2 = df.groupby(y_param)['score'].agg(['mean', 'std']).reset_index()
        grouped_p2 = grouped_p2.sort_values(y_param)
        ax_p2.plot(grouped_p2[y_param], grouped_p2['mean'], 'r-o', linewidth=2, markersize=7)
        ax_p2.fill_between(grouped_p2[y_param],
                          grouped_p2['mean'] - grouped_p2['std'],
                          grouped_p2['mean'] + grouped_p2['std'],
                          alpha=0.3, color='red')
        ax_p2.set_xlabel(y_param, fontsize=11, fontweight='bold')
        ax_p2.set_ylabel('Score (|% growth|)', fontsize=11, fontweight='bold')
        ax_p2.set_title(f'Effect of {y_param} on Growth Rate', fontsize=12, fontweight='bold')
        ax_p2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Mapa ciepła zapisana: {output_file}")
        plt.close()
    
    def check_optimum_not_at_edge(self):
        """Sprawdź czy optimum nie na krawędzi."""
        if not self.best_params:
            return False
        
        at_edge = False
        for param_name, grid_values in self.param_grid.items():
            param_val = self.best_params[param_name]
            
            if np.isclose(param_val, grid_values[0]):
                print(f"⚠️  {param_name} = {param_val} (at MIN boundary)")
                at_edge = True
            elif np.isclose(param_val, grid_values[-1]):
                print(f"⚠️  {param_name} = {param_val} (at MAX boundary)")
                at_edge = True
        
        if not at_edge:
            print(f"✓ Optimum jest wewnątrz siatki parametrów")
        
        return not at_edge


# ============================================================================
# FUNKCJE OCENY - FULL SCALE (50,000 agentów, 50 lat)
# ============================================================================

def full_scale_scoring(fertility_multiplier, mortality_multiplier):
    """
    Funkcja oceny dla pełnej skali.
    
    UWAGA: Ta funkcja będzie bardzo wolna ze względu na:
    - 50,000 agentów
    - 50 lat symulacji
    - Model choroby
    - Obliczenia demograficzne
    
    Czas wykonania: ~5-10 minut na kombinację
    """
    try:
        print(f"\n  → Running full-scale sim: fertility={fertility_multiplier:.2f}, "
              f"mortality={mortality_multiplier:.2f}")
        
        start = time.time()
        
        # Inicjalizuj model
        disease_model = DiseaseModel()
        engine = SimulationEngine(disease_model=disease_model, seed=42)
        
        # Ustaw parametry
        engine.fertility_rate = fertility_multiplier
        engine.mortality_multiplier = mortality_multiplier
        engine.household_split_probability = 0.001
        
        # Stwórz populację
        print(f"    Creating 50,000 synthetic agents...")
        engine._create_synthetic_population(50000)
        initial_pop = len([c for c in engine.citizens.values() if c.alive])
        
        # Uruchom symulację
        print(f"    Running 50-year simulation (600 months)...")
        engine.run(months=600)
        
        # Oblicz wynik
        final_pop = len([c for c in engine.citizens.values() if c.alive])
        annual_growth = ((final_pop - initial_pop) / initial_pop) * 100 / 50
        
        # Szukamy minimum - idealnie by wzrost był bliski 0
        score = abs(annual_growth)
        
        elapsed = time.time() - start
        print(f"    ✓ Done in {elapsed:.1f}s: initial={initial_pop}, final={final_pop}, "
              f"annual_growth={annual_growth:.2f}%, score={score:.2f}")
        
        return score
        
    except Exception as e:
        print(f"    ✗ ERROR: {e}")
        return 10000


# ============================================================================
# MAIN EXECUTION
# ============================================================================
if __name__ == "__main__":
    
    # Pytaj czy uruchomić tak dużą symulację
    print("\n" + "="*80)
    print("FULL-SCALE GRID SEARCH: 50,000 Agents, 50 Years")
    print("="*80)
    print("\n⚠️  WARNING: This will take a very long time!")
    print("  - 100 combinations (10x10 grid)")
    print("  - ~5-10 minutes per combination")
    print("  - Total: ~500-1000 minutes (~8-16 hours)")
    print("\nESTIMATED DURATION: 8-16 hours of computation\n")
    
    response = input("Continue? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("Aborted.")
        exit(0)
    
    # Konfiguracja - ROZSZERZONE PARAMETRY
    param_grid = {
        "fertility_multiplier": np.linspace(0.1, 2.8, 10),
        "mortality_multiplier": np.linspace(0.1, 2.8, 10),
    }
    
    # Uruchom optimalizację
    optimizer = FullScaleGridSearch(
        param_grid=param_grid,
        scoring_function=full_scale_scoring,
        verbose=True
    )
    
    best_params, best_score = optimizer.optimize()
    
    # Analiza wyników
    print()
    optimizer.check_optimum_not_at_edge()
    print()
    
    # Zapisz
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    optimizer.save_results(f"gridsearch_fullscale_{timestamp}.json")
    
    # Wizualizacja
    print()
    optimizer.create_heatmap(f'heatmap_fullscale_50k_50y_{timestamp}.png')
    
    # Top wyniki
    print("\nTOP 10 RESULTS:")
    print("-"*80)
    df = optimizer.get_results_dataframe()
    for i, (idx, row) in enumerate(df.head(10).iterrows(), 1):
        print(f"{i:2d}. Fertility: {row['fertility_multiplier']:6.2f} | "
              f"Mortality: {row['mortality_multiplier']:6.2f} | "
              f"Score: {row['score']:7.2f}")
    print()
