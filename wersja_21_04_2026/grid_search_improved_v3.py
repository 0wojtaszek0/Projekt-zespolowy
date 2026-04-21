"""
Grid Search Optimization V3 - Ulepszona wersja
- Rozszerzone zakresy parametrów (10 wartości w każdym kierunku)
- Mapa ciepła w matplotlib z kolorami 'bwr'
- Rysowanie funkcji birth_rate i mortality_rate
- Szukanie minimum (niedodatni wzrost populacji)
- Równomierne podziały etykiet na osiach
- Sprawdzenie czy punkt optymalny nie pada na brzegu
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from itertools import product
from simulation_engine import SimulationEngine
from disease_model import DiseaseModel
import json
from datetime import datetime


class GridSearchImprovedV3:
    """
    Ulepszona wersja Grid Search z lepszą wizualizacją i obsługą mapy ciepła.
    """
    
    def __init__(self, param_grid, scoring_function, n_iter=1, verbose=True):
        """
        Args:
            param_grid: Dict z parametrami do optymalizacji
            scoring_function: Funkcja ewaluacyjna
            n_iter: Liczba iteracji
            verbose: Drukuj informacje
        """
        self.param_grid = param_grid
        self.scoring_function = scoring_function
        self.n_iter = n_iter
        self.verbose = verbose
        self.results = []
        self.best_params = None
        self.best_score = float('inf')  # Szukamy MINIMUM
        self.lowest_score = float('inf')
        self.highest_score = -float('inf')

    def optimize(self):
        """Przeprowadź grid search i zbierz wyniki."""
        param_names = list(self.param_grid.keys())
        param_values = list(self.param_grid.values())
        
        total_combinations = np.prod([len(v) for v in param_values])
        
        if self.verbose:
            print("\n" + "="*70)
            print("GRID SEARCH OPTIMIZATION V3 - ULEPSZONA WERSJA")
            print("="*70)
            print(f"Parametry: {param_names}")
            print(f"Wartości param 1: {[f'{x:.3f}' for x in param_values[0]]}")
            print(f"Wartości param 2: {[f'{x:.3f}' for x in param_values[1]]}")
            print(f"Razem kombinacji: {int(total_combinations)}")
            print(f"Optymalizacja: MINIMUM (szukamy najmniejszej wartości)")
            print("="*70 + "\n")
        
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
                    
                    # Tracking dla minimum
                    if score < self.best_score:
                        self.best_score = score
                        self.best_params = params
                    
                    self.lowest_score = min(self.lowest_score, score)
                    self.highest_score = max(self.highest_score, score)
                    
                    if self.verbose and (current_combo % 10 == 0 or current_combo == 1):
                        param_str = " | ".join([f"{name}: {val:.3f}" for name, val in params.items()])
                        print(f"[{current_combo:3d}/{int(total_combinations)}] {param_str} | Score: {score:8.2f}")
                
                except Exception as e:
                    print(f"BŁĄD w kombinacji {params}: {e}")
                    self.results.append({
                        "combo": current_combo,
                        "iteration": iteration + 1,
                        "params": params,
                        "score": 10000,
                        "error": str(e)
                    })
        
        if self.verbose:
            print("\n" + "="*70)
            print("REZULTAT KOŃCOWY")
            print("="*70)
            print(f"Najlepsze parametry: {self.best_params}")
            print(f"Najlepszy score (minimum): {self.best_score:.2f}")
            print(f"Zakres wyników: [{self.lowest_score:.2f} ... {self.highest_score:.2f}]")
            print("="*70 + "\n")
        
        return self.best_params, self.best_score
    
    def get_results_dataframe(self):
        """Zwróć wyniki jako DataFrame."""
        if not self.results:
            return None
        df = pd.DataFrame(self.results)
        # Rozpakuj parametry w osobne kolumny
        params_df = pd.json_normalize(df['params'])
        df = pd.concat([df.drop('params', axis=1), params_df], axis=1)
        return df.sort_values('score')
    
    def save_results(self, filename="gridsearch_results_v3.json"):
        """Zapisz wyniki do JSON."""
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
            print(f"✓ Zapisano wyniki do: {filename}")
    
    def create_heatmap_with_functions(self, output_file='heatmap_gridsearch_improved.png'):
        """
        Stwórz mapę ciepła z matplotlib z kolorami 'bwr', narysuj funkcje i ich wzory.
        """
        if not self.results:
            print("Brak wyników. Uruchom optimize() najpierw.")
            return
        
        df = self.get_results_dataframe()
        
        param_names = list(self.param_grid.keys())
        x_param = param_names[0]
        y_param = param_names[1]
        
        x_values = sorted(df[x_param].unique())
        y_values = sorted(df[y_param].unique())
        
        # Stwórz macierz wyników
        matrix = np.full((len(y_values), len(x_values)), np.nan)
        
        for i, y_val in enumerate(y_values):
            for j, x_val in enumerate(x_values):
                mask = (df[x_param] == x_val) & (df[y_param] == y_val)
                if mask.any():
                    matrix[i, j] = df[mask]['score'].mean()
        
        # Stwórz figurę z subplotami
        fig = plt.figure(figsize=(18, 12))
        
        # 1. MAPA CIEPŁA (główny plot)
        ax_heatmap = plt.subplot(2, 3, (1, 4))
        
        # Normalizacja dla 'bwr' (Blue = minimalne, Red = maksymalne)
        norm = Normalize(vmin=self.lowest_score, vmax=self.highest_score)
        
        im = ax_heatmap.imshow(
            matrix, 
            cmap='bwr', 
            norm=norm,
            aspect='auto',
            origin='lower',
            extent=[x_values[0], x_values[-1], y_values[0], y_values[-1]],
            interpolation='nearest'
        )
        
        # Ustaw etykiety osi z równomiernym podziałem (POPRAWIONE - rzeczywiste wartości na osiach)
        self._set_equal_ticks_fixed(ax_heatmap, x_param, y_param, x_values, y_values)
        
        ax_heatmap.set_xlabel(x_param, fontsize=12, fontweight='bold')
        ax_heatmap.set_ylabel(y_param, fontsize=12, fontweight='bold')
        ax_heatmap.set_title(f'Heatmap Gridsearch - Szukanie MINIMUM\n(Niebieskie = lepsze, Czerwone = gorsze)', 
                            fontsize=14, fontweight='bold')
        
        # Kolorbar
        cbar = plt.colorbar(im, ax=ax_heatmap)
        cbar.set_label('Score (niska = lepsza)', rotation=270, labelpad=20)
        
        # Zaznacz punkt optymalny
        if self.best_params:
            x_opt = self.best_params[x_param]
            y_opt = self.best_params[y_param]
            ax_heatmap.plot(x_opt, y_opt, 'g*', markersize=25, markeredgecolor='darkgreen', markeredgewidth=1.5,
                           label=f'Optimum: {self.best_score:.2f}', zorder=5)
            ax_heatmap.legend(fontsize=10, loc='upper right')
        
        # 2. FUNKCJA FERTILITY (obok heatmapy)
        ax_birth = plt.subplot(2, 3, 2)
        fertility_param = x_param if 'fertility' in x_param else y_param
        self._plot_parameter_with_formula(ax_birth, df, fertility_param, 'score', 'Fertility')
        
        # 3. FUNKCJA MORTALITY (obok fertility)
        ax_mort = plt.subplot(2, 3, 3)
        mortality_param = y_param if 'mortality' in y_param else x_param
        self._plot_parameter_with_formula(ax_mort, df, mortality_param, 'score', 'Mortality')
        
        # 4. SCATTER PLOT FERTILITY
        ax_scatter_birth = plt.subplot(2, 3, 5)
        fertility_data = df.groupby(fertility_param)['score'].agg(['mean', 'std', 'count']).reset_index()
        ax_scatter_birth.scatter(fertility_data[fertility_param], fertility_data['mean'], s=100, alpha=0.6, color='blue')
        ax_scatter_birth.set_xlabel(fertility_param, fontsize=10)
        ax_scatter_birth.set_ylabel('Score', fontsize=10)
        ax_scatter_birth.set_title('Zależność Fertility - Score', fontsize=11, fontweight='bold')
        ax_scatter_birth.grid(True, alpha=0.3)
        
        # Dodaj formułę na wykresie fertility
        formula_birth = r'$Birth\_Rate(x) = base\_rate \times fertility\_multiplier$'
        ax_scatter_birth.text(0.05, 0.95, formula_birth, transform=ax_scatter_birth.transAxes,
                             fontsize=9, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        # 5. SCATTER PLOT MORTALITY
        ax_scatter_mort = plt.subplot(2, 3, 6)
        mortality_data = df.groupby(mortality_param)['score'].agg(['mean', 'std', 'count']).reset_index()
        ax_scatter_mort.scatter(mortality_data[mortality_param], mortality_data['mean'], s=100, alpha=0.6, color='red')
        ax_scatter_mort.set_xlabel(mortality_param, fontsize=10)
        ax_scatter_mort.set_ylabel('Score', fontsize=10)
        ax_scatter_mort.set_title('Zależność Mortality - Score', fontsize=11, fontweight='bold')
        ax_scatter_mort.grid(True, alpha=0.3)
        
        # Dodaj formułę na wykresie mortality
        formula_mort = r'$Mortality\_Rate(x) = base\_rate \times mortality\_multiplier$'
        ax_scatter_mort.text(0.05, 0.95, formula_mort, transform=ax_scatter_mort.transAxes,
                            fontsize=9, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Mapa ciepła z funkcjami zapisana do: {output_file}")
        plt.close()
    
    def _set_equal_ticks(self, ax, x_param, y_param, x_values, y_values):
        """Ustaw równomierne podziały etykiet na osiach (DEPRECATED - use _set_equal_ticks_fixed)."""
        # Oś X
        n_ticks = min(6, len(x_values))
        step = max(1, len(x_values) // (n_ticks - 1))
        x_tick_positions = np.arange(0, len(x_values), step)
        x_tick_labels = [f'{x_values[i]:.3f}' if i < len(x_values) else '' for i in x_tick_positions]
        
        ax.set_xticks(x_tick_positions)
        ax.set_xticklabels(x_tick_labels, rotation=45, ha='right')
        
        # Oś Y
        n_ticks = min(6, len(y_values))
        step = max(1, len(y_values) // (n_ticks - 1))
        y_tick_positions = np.arange(0, len(y_values), step)
        y_tick_labels = [f'{y_values[i]:.3f}' if i < len(y_values) else '' for i in y_tick_positions]
        
        ax.set_yticks(y_tick_positions)
        ax.set_yticklabels(y_tick_labels)
    
    def _set_equal_ticks_fixed(self, ax, x_param, y_param, x_values, y_values):
        """
        NAPRAWIONE: Ustaw równomierne podziały etykiet na osiach.
        Ticksy są ustawiane we RZECZYWISTYCH współrzędnych, nie indeksach!
        """
        # Oś X - część wartości
        n_ticks = min(7, len(x_values))
        indices = np.linspace(0, len(x_values) - 1, n_ticks, dtype=int)
        x_tick_positions = [x_values[i] for i in indices]
        x_tick_labels = [f'{val:.3f}' for val in x_tick_positions]
        
        ax.set_xticks(x_tick_positions)
        ax.set_xticklabels(x_tick_labels, rotation=45, ha='right', fontsize=9)
        
        # Oś Y - część wartości
        n_ticks = min(7, len(y_values))
        indices = np.linspace(0, len(y_values) - 1, n_ticks, dtype=int)
        y_tick_positions = [y_values[i] for i in indices]
        y_tick_labels = [f'{val:.3f}' for val in y_tick_positions]
        
        ax.set_yticks(y_tick_
    
    def _plot_parameter_with_formula(self, ax, df, param, metric, param_type):
        """
        NAPRAWIONE: Sprawdź czy punkt optymalny nie pada na krawędź siatki.
        Jeśli pada na brzeg, ostrzeż użytkownika i zasugeruj rozszerzenie zakresu.
        """
        if not self.best_params:
            print("⚠ Brak danych do sprawdzenia")
            return False
        
        at_edge = False
        edge_info = []
        
        for param_name, param_grid_values in self.param_grid.items():
            param_val = self.best_params[param_name]
            
            # Sprawdź czy to pierwsza lub ostatnia wartość
            if np.isclose(param_val, param_grid_values[0]):
                at_edge = True
                edge_info.append(f"  - '{param_name}' na DOLNEJ krawędzi ({param_val:.5f})")
                print(f"⚠ OSTRZEŻENIE: Parametr '{param_name}' na dolnej krawędzi: {param_val:.5f}")
                print(f"  Sugestia: Zmniejsz minimalną wartość dla '{param_name}'")
                
            elif np.isclose(param_val, param_grid_values[-1]):
                at_edge = True
                edge_info.append(f"  - '{param_name}' na GÓRNEJ krawędzi ({param_val:.5f})")
                print(f"⚠ OSTRZEŻENIE: Parametr '{param_name}' na górnej krawędzi: {param_val:.5f}")
                print(f"  Sugestia: Zwiększ maksymalną wartość dla '{param_name}'")
            else:
                print(f"✓ Parametr '{param_name}' wewnątrz zakresu [{param_grid_values[0]:.5f}, {param_grid_values[-1]:.5f}]")
        
        if not at_edge:
            print(f"\n✅ PUNKT OPTYMALNY JEST WEWNĄTRZ SIATKI - WYNIKI SĄ WIARYGODNE")
        else:
            print(f"\n❌ PUNKT OPTYMALNY NA BRZEGU SIATKI!")
            print(f"    Zalecane działania:")
            for info in edge_info:
                print(info)
            print(f"    Rozszerz zakresy w param_grid i uruchom grid search ponownie.")
        
        return not at_edgue, alpha=0.3)
        
        # Dodaj wzór
        if param_type == 'Fertility':
            formula = r'$BR(t) = 0.03 \times multiplier$'
            box_color = 'lightblue'
        else:
            formula = r'$MR(t) = 0.0015 \times multiplier$'
            box_color = 'lightcoral'
        
        ax.text(0.5, 0.95, formula, transform=ax.transAxes,
               fontsize=10, verticalalignment='top', horizontalalignment='center',
               bbox=dict(boxstyle='round', facecolor=box_color, alpha=0.8, edgecolor='black', linewidth=1.5))positions)
        ax.set_yticklabels(y_tick_labels, fontsize=9)
    
    def _plot_parameter_function(self, ax, df, param, metric):
        """Narysuj funkcję wpływu parametru na metrykę."""
        # Sprawdź czy kolumna istnieje (małe litery)
        if metric not in df.columns:
            if metric.lower() in df.columns:
                metric = metric.lower()
            elif metric.capitalize() in df.columns:
                metric = metric.capitalize()
        grouped = df.groupby(param)[metric].agg(['mean', 'std']).reset_index()
        grouped = grouped.sort_values(param)
        
        ax.plot(grouped[param], grouped['mean'], 'b-o', linewidth=2, markersize=6, label='Średnia')
        ax.fill_between(grouped[param], 
                       grouped['mean'] - grouped['std'], 
                       grouped['mean'] + grouped['std'],
                       alpha=0.3, label='±1 std')
        
        ax.set_xlabel(param, fontsize=10)
        ax.set_ylabel(metric, fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=9)
    
    def check_optimum_not_at_edge(self):
        """Sprawdź czy punkt optymalny nie pada na krawędź siatki."""
        if not self.best_params:
            return False
        
        for param_name, param_grid_values in self.param_grid.items():
            param_val = self.best_params[param_name]
            
            # Sprawdź czy to pierwsza lub ostatnia wartość
            if np.isclose(param_val, param_grid_values[0]):
                print(f"⚠ UWAGA: Parametr '{param_name}' na dolnej krawędzi: {param_val}")
                return False
            elif np.isclose(param_val, param_grid_values[-1]):
                print(f"⚠ UWAGA: Parametr '{param_name}' na górnej krawędzi: {param_val}")
                return False
        
        print(f"✓ Punkt optymalny jest wewnątrz siatki parametrów")
        return True


# ============================================================================
# PRZYKŁAD UŻYCIA
# ============================================================================
if __name__ == "__main__":
    def simulation_scoring_function(fertility_multiplier, mortality_multiplier):
        """
        Funkcja ewaluacyjna - szuka MINIMUM.
        Ujemne wartości = dobra (populacja się zmniejsza kontrolowanie)
        Dodatnie duże = złe (populacja rośnie bezControlnie)
        """
        try:
            birth_rate = 0.03
            mortality_rate = 0.0015
            
            initial_population = 50000
            final_population = initial_population

            for year in range(50):
                births = final_population * birth_rate * fertility_multiplier
                deaths = final_population * mortality_rate * mortality_multiplier
                final_population += births - deaths

                if final_population < 0:
                    final_population = 0
                    break

            # Score: zmiana populacji (% roczne średnio)
            score = ((final_population - initial_population) / initial_population) * 100 / 50
            
            # Szukamy minimum - idealne by było blisko 0 (stabilna populacja)
            # Może być ujemne (populacja spada) lub małe dodatnie (rośnie wolno)
            return abs(score)  # Abs - szukamy bliski 0
            
        except Exception as e:
            print(f"Błąd: {e}")
            return 1000  # Duża kara za błędy
    
    # ====== KONFIGURACJA PARAMETRÓW ======
    # ROZSZERZONE zakresy - szukaj minimum wewnątrz gridu!
    # Jeśli punkt pada na brzeg, rozszerz zakresy jeszcze bardziej
    
    param_grid = {
        "fertility_multiplier": np.linspace(0.1, 3.5, 12),    # 12 wartości - rozprzestrzenione szerzej
        "mortality_multiplier": np.linspace(0.1, 3.5, 12),    # 12 wartości
    }
    
    print("\n" + "="*80)
    print("GRIDSEARCH KONFIGURACJA V3 (ULEPSZONA) - Z POPRAWKAMI")
    print("="*80)
    print(f"Fertility multiplier zakresy: {np.linspace(0.1, 3.5, 12)[0]:.3f} ... {np.linspace(0.1, 3.5, 12)[-1]:.3f}")
    print(f"  Wartości: {[f'{x:.3f}' for x in param_grid['fertility_multiplier']]}")
    print(f"\nMortality multiplier zakresy: {np.linspace(0.1, 3.5, 12)[0]:.3f} ... {np.linspace(0.1, 3.5, 12)[-1]:.3f}")
    print(f"  Wartości: {[f'{x:.3f}' for x in param_grid['mortality_multiplier']]}")
    print(f"\nRazem kombinacji: {int(np.prod([len(v) for v in param_grid.values()]))}")
    print("="*80 + "\n")
    
    # Uruchom grid search
    optimizer = GridSearchImprovedV3(
        param_grid=param_grid,
        scoring_function=simulation_scoring_function,
        n_iter=1,
        verbose=True
    )
    
    best_params, best_score = optimizer.optimize()
    
    # Sprawdź czy optimum nie na krawędzi
    print()
    optimizer.check_optimum_not_at_edge()
    print()
    
    # Zapisz wyniki
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    optimizer.save_results(f"gridsearch_results_v3_{timestamp}.json")
    
    # Stwórz mapę ciepła
    print()
    optimizer.create_heatmap_with_functions(f'heatmap_gridsearch_v3_{timestamp}.png')
    
    # Wypisz Top 5
    print("\nTOP 5 WYNIKÓW (MINIMUM):")
    print("-" * 70)
    df_results = optimizer.get_results_dataframe()
    for i, (idx, row) in enumerate(df_results.head(5).iterrows(), 1):
        param_str = " | ".join([f"{col}: {row[col]:.3f}" for col in ['fertility_multiplier', 'mortality_multiplier']])
        print(f"{i}. Score: {row['score']:8.2f} | {param_str}")
    print()
