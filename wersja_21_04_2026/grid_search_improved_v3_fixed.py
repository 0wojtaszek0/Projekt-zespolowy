"""
Grid Search Optimization V3 - POPRAWIONA WERSJA
✅ Fixes:
1) PODZIAŁKI NA OSIACH HEATMAPY - rzeczywiste wartości, nie indeksy
2) PUNKT OPTYMALNY NA BRZEGU - lepszy komunikat i sugestie rozszerzenia zakresu
3) WYKRESY FUNKCJI z WZORAMI - Birth Rate i Mortality Rate z formułami matematycznymi
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from itertools import product
import json
from datetime import datetime


class GridSearchImprovedV3Fixed:
    """
    Ulepszona wersja Grid Search z poprawkami wizualizacji.
    """
    
    def __init__(self, param_grid, scoring_function, n_iter=1, verbose=True):
        self.param_grid = param_grid
        self.scoring_function = scoring_function
        self.n_iter = n_iter
        self.verbose = verbose
        self.results = []
        self.best_params = None
        self.best_score = float('inf')
        self.lowest_score = float('inf')
        self.highest_score = -float('inf')

    def optimize(self):
        """Przeprowadź grid search."""
        param_names = list(self.param_grid.keys())
        param_values = list(self.param_grid.values())
        
        total_combinations = np.prod([len(v) for v in param_values])
        
        if self.verbose:
            print("\n" + "="*70)
            print("GRID SEARCH OPTIMIZATION V3 - FIXED")
            print("="*70)
            print(f"Parametry: {param_names}")
            print(f"Razem kombinacji: {int(total_combinations)}")
            print("="*70 + "\n")
        
        current_combo = 0
        
        for iteration in range(self.n_iter):
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

                    self.lowest_score = min(self.lowest_score, score)
                    self.highest_score = max(self.highest_score, score)

                    if self.verbose and (current_combo % max(1, int(total_combinations/10)) == 0 or current_combo == 1):
                        param_str = " | ".join([f"{name}: {val:.3f}" for name, val in params.items()])
                        print(f"[{current_combo:3d}/{int(total_combinations)}] {param_str} | Score: {score:.2f}")
                
                except Exception as e:
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
    
    def create_heatmap_with_functions(self, output_file='heatmap_gridsearch_v3_fixed.png'):
        """
        POPRAWIONA: Stwórz mapę ciepła z matplotlib z kolorami 'bwr', narysuj funkcje i ich wzory.
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
        
        # Stwórz figurę
        fig = plt.figure(figsize=(18, 12))
        
        # ===== MAPA CIEPŁA =====
        ax_heatmap = plt.subplot(2, 3, (1, 4))
        
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
        
        # ✅ FIX 1: PODZIAŁKI - rzeczywiste wartości na osiach
        self._set_ticks_with_real_values(ax_heatmap, x_values, y_values)
        
        ax_heatmap.set_xlabel(x_param, fontsize=12, fontweight='bold')
        ax_heatmap.set_ylabel(y_param, fontsize=12, fontweight='bold')
        ax_heatmap.set_title(f'Heatmap Gridsearch - Szukanie MINIMUM\n(Niebieskie = lepsze, Czerwone = gorsze)', 
                            fontsize=14, fontweight='bold')
        
        cbar = plt.colorbar(im, ax=ax_heatmap)
        cbar.set_label('Score (niska = lepsza)', rotation=270, labelpad=20)
        
        # ✅ FIX 2: Zaznacz punkt optymalny
        if self.best_params:
            x_opt = self.best_params[x_param]
            y_opt = self.best_params[y_param]
            ax_heatmap.plot(x_opt, y_opt, 'g*', markersize=25, markeredgecolor='darkgreen', 
                           markeredgewidth=1.5, label=f'Optimum: {self.best_score:.2f}', zorder=5)
            ax_heatmap.legend(fontsize=11, loc='upper right')
        
        # ===== BIRTH RATE FUNCTION =====
        ax_birth = plt.subplot(2, 3, 2)
        birth_param = x_param if 'birth' in x_param or 'birth_rate' in x_param else y_param
        self._plot_with_formula(ax_birth, df, birth_param, 'score', 'Birth Rate')
        
        # ===== MORTALITY FUNCTION =====
        ax_mort = plt.subplot(2, 3, 3)
        mortality_param = y_param if 'mortality' in y_param or 'mortality_rate' in y_param else x_param
        self._plot_with_formula(ax_mort, df, mortality_param, 'score', 'Mortality Rate')
        
        # ===== SCATTER BIRTH =====
        ax_scatter_birth = plt.subplot(2, 3, 5)
        birth_data = df.groupby(birth_param)['score'].agg(['mean', 'std']).reset_index()
        ax_scatter_birth.scatter(birth_data[birth_param], birth_data['mean'], 
                    s=120, alpha=0.7, color='blue', edgecolors='darkblue', linewidth=1.5)
        ax_scatter_birth.set_xlabel(birth_param, fontsize=10, fontweight='bold')
        ax_scatter_birth.set_ylabel('Score', fontsize=10, fontweight='bold')
        ax_scatter_birth.set_title('Birth Rate - Score Dependency', fontsize=11, fontweight='bold')
        ax_scatter_birth.grid(True, alpha=0.3)

        formula_birth = r'$BR(t) = birth\_rate$'
        ax_scatter_birth.text(0.5, 0.95, formula_birth, transform=ax_scatter_birth.transAxes,
                     fontsize=9, verticalalignment='top', horizontalalignment='center',
                     bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.85, 
                           edgecolor='blue', linewidth=1.5))
        
        # ===== SCATTER MORTALITY =====
        ax_scatter_mort = plt.subplot(2, 3, 6)
        mortality_data = df.groupby(mortality_param)['score'].agg(['mean', 'std']).reset_index()
        ax_scatter_mort.scatter(mortality_data[mortality_param], mortality_data['mean'], 
                               s=120, alpha=0.7, color='red', edgecolors='darkred', linewidth=1.5)
        ax_scatter_mort.set_xlabel(mortality_param, fontsize=10, fontweight='bold')
        ax_scatter_mort.set_ylabel('Score', fontsize=10, fontweight='bold')
        ax_scatter_mort.set_title('Mortality - Score Dependency', fontsize=11, fontweight='bold')
        ax_scatter_mort.grid(True, alpha=0.3)
        
        formula_mort = r'$MR(t) = mortality\_rate$'
        ax_scatter_mort.text(0.5, 0.95, formula_mort, transform=ax_scatter_mort.transAxes,
                            fontsize=9, verticalalignment='top', horizontalalignment='center',
                            bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.85, 
                                    edgecolor='red', linewidth=1.5))
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Mapa ciepła z funkcjami zapisana do: {output_file}")
        plt.close()
    
    def _set_ticks_with_real_values(self, ax, x_values, y_values):
        """
        ✅ FIX 1: Ustaw ticksy we RZECZYWISTYCH współrzędnych, nie indeksach!
        """
        # Oś X
        n_ticks_x = min(7, len(x_values))
        indices_x = np.linspace(0, len(x_values) - 1, n_ticks_x, dtype=int)
        x_positions = [x_values[i] for i in indices_x]

        # Wybierz format etykiet sensownie zależnie od skali (czyli czy wartości >=1)
        max_x = max(abs(v) for v in x_values) if len(x_values) > 0 else 1.0
        if max_x >= 1:
            fmt_x = '{:.1f}'
        elif max_x >= 0.01:
            fmt_x = '{:.3f}'
        else:
            fmt_x = '{:.4f}'

        x_labels = [fmt_x.format(val) for val in x_positions]
        ax.set_xticks(x_positions)
        ax.set_xticklabels(x_labels, rotation=45, ha='right', fontsize=9)

        # Oś Y
        n_ticks_y = min(7, len(y_values))
        indices_y = np.linspace(0, len(y_values) - 1, n_ticks_y, dtype=int)
        y_positions = [y_values[i] for i in indices_y]

        max_y = max(abs(v) for v in y_values) if len(y_values) > 0 else 1.0
        if max_y >= 1:
            fmt_y = '{:.1f}'
        elif max_y >= 0.01:
            fmt_y = '{:.3f}'
        else:
            fmt_y = '{:.4f}'

        y_labels = [fmt_y.format(val) for val in y_positions]
        ax.set_yticks(y_positions)
        ax.set_yticklabels(y_labels, fontsize=9)
    
    def _plot_with_formula(self, ax, df, param, metric, param_type):
        """
        Narysuj funkcję z wzorem matematycznym.
        """
        grouped = df.groupby(param)[metric].agg(['mean', 'std']).reset_index()
        grouped = grouped.sort_values(param)
        
        color = '#1f77b4' if 'Birth' in param_type or 'birth' in param_type else '#d62728'
        
        ax.plot(grouped[param], grouped['mean'], 'o-', linewidth=2.5, markersize=7, 
               color=color, alpha=0.8, label='Mean')
        ax.fill_between(grouped[param], 
                       grouped['mean'] - grouped['std'], 
                       grouped['mean'] + grouped['std'],
                       alpha=0.2, color=color)
        
        ax.set_xlabel(param, fontsize=10, fontweight='bold')
        ax.set_ylabel('Score', fontsize=10, fontweight='bold')
        ax.set_title(f'{param_type} Parameter Impact', fontsize=11, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=9)
        
        # Dodaj wzór matematyczny widoczny na wykresie
        if 'Birth' in param_type or 'birth' in param_type:
            formula = r'$BR(t) = birth\_rate$'
            box_color = 'lightblue'
        else:
            formula = r'$MR(t) = mortality\_rate$'
            box_color = 'lightcoral'

        ax.text(0.5, 0.95, formula, transform=ax.transAxes,
               fontsize=10, verticalalignment='top', horizontalalignment='center',
               bbox=dict(boxstyle='round', facecolor=box_color, alpha=0.8, edgecolor='black', linewidth=1.0))

    # (Automatyczne rozszerzanie zakresów usunięte - przywrócono prosty przebieg)

    # (Nudge dla zer usunięty - przywrócono prosty przebieg)
    
    def check_optimum_not_at_edge(self):
        """
        ✅ FIX 2: Sprawdź czy punkt optymalny pada na brzeg siatki.
        Jeśli tak, ostrzeż i zasugeruj rozszerzenie zakresu.
        """
        if not self.best_params:
            return False
        
        print("\n" + "="*70)
        print("SPRAWDZENIE PUNKTU OPTYMALNEGO")
        print("="*70)
        
        at_edge = False
        
        for param_name, param_grid_values in self.param_grid.items():
            param_val = self.best_params[param_name]
            param_min = param_grid_values[0]
            param_max = param_grid_values[-1]
            
            print(f"\n📊 Parametr: {param_name}")
            print(f"   Zakres: [{param_min:.5f}, {param_max:.5f}]")
            print(f"   Wartość: {param_val:.5f}", end="")
            
            if np.isclose(param_val, param_min, rtol=1e-5):
                print(" ❌ NA DOLNEJ KRAWĘDZI!")
                print(f"   ⚠️ OSTRZEŻENIE: Optymalny parametr na minimalnej wartości")
                # Sugeruj rozszerzenie zakresu proporcjonalnie do obecnego kroku
                delta = param_max - param_min
                new_min = max(0.0, param_min - delta)
                new_max = param_max + delta
                print(f"   → Sugerowane rozszerzenie: np.linspace({new_min:.4f}, {new_max:.4f}, ...)")
                at_edge = True
            elif np.isclose(param_val, param_max, rtol=1e-5):
                print(" ❌ NA GÓRNEJ KRAWĘDZI!")
                print(f"   ⚠️ OSTRZEŻENIE: Optymalny parametr na maksymalnej wartości")
                delta = param_max - param_min
                new_min = max(0.0, param_min - delta)
                new_max = param_max + delta
                print(f"   → Sugerowane rozszerzenie: np.linspace({new_min:.4f}, {new_max:.4f}, ...)")
                at_edge = True
            else:
                print(" ✅ WEWNĄTRZ ZAKRESU")
        
        print("\n" + "="*70)
        if not at_edge:
            print("✅ SUKCES: Punkt optymalny jest wewnątrz siatki parametrów!")
            print("   Wyniki są WIARYGODNE - optymum znalezione w wnętrzu przestrzeni poszukiwań.")
        else:
            print("❌ UWAGA: Punkt optymalny pada na BRZEG siatki!")
            print("   Wyniki mogą być NIEWIARYGODNE - optymum może być poza zakresem.")
            print("   → Zalecane działanie: Rozszerz zakresy param_grid i uruchom ponownie")
        print("="*70 + "\n")
        
        return not at_edge


# ============================================================================
# PRZYKŁAD UŻYCIA
# ============================================================================
if __name__ == "__main__":
    def simulation_scoring_function(birth_rate, mortality_rate):
        """
        Funkcja ewaluacyjna - przyjmuje BEZWZGLĘDNE birth_rate i mortality_rate.
        Liczy zmianę populacji po 50 latach i zwraca absolutną średnioroczną zmianę (%) jako score.
        """
        try:
            initial_population = 50000
            final_population = initial_population

            for year in range(50):
                births = final_population * birth_rate
                deaths = final_population * mortality_rate
                final_population += births - deaths

                if final_population < 0:
                    final_population = 0
                    break

            # Zmieniony score na bezwzględną zmianę procentową
            score = abs(((final_population - initial_population) / initial_population) * 100)
            return score

        except Exception:
            return 1000

    # ====== KONFIGURACJA PARAMETRÓW (BEZWZGLĘDNE STOPY) ======
    # birth_rate: roczna stopa narodzin (np. 0.03 = 3%)
    # mortality_rate: roczna stopa zgonów (np. 0.0015 = 0.15%)
    param_grid = {
        "birth_rate": np.linspace(0.0001, 0.0080, 10),     # 0.01% ... 0.8% (10 punktów)
        "mortality_rate": np.linspace(0.0005, 0.0060, 10), # 0.05% ... 0.60% (10 punktów)
    }

    print("\n" + "="*80)
    print("GRIDSEARCH V3 - BIRTH_RATE & MORTALITY_RATE")
    print("="*80)
    print(f"Birth rate values: {[f'{x:.4f}' for x in param_grid['birth_rate']]}")
    print(f"Mortality rate values: {[f'{x:.5f}' for x in param_grid['mortality_rate']]}")
    print(f"Total combinations: {int(np.prod([len(v) for v in param_grid.values()]))}")
    print("="*80 + "\n")

    # Uruchom grid search
    optimizer = GridSearchImprovedV3Fixed(
        param_grid=param_grid,
        scoring_function=simulation_scoring_function,
        n_iter=1,
        verbose=True
    )

    # Uruchom jednorazowo grid search i zapisz wyniki
    best_params, best_score = optimizer.optimize()
    optimizer.check_optimum_not_at_edge()

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    optimizer.save_results(f"gridsearch_results_v3_fixed_{timestamp}.json")

    # Stwórz mapę z funkcjami i wzorami
    print()
    optimizer.create_heatmap_with_functions(f'heatmap_gridsearch_v3_fixed_{timestamp}.png')

    # Wypisz Top 5
    print("\nTOP 5 WYNIKÓW:")
    print("-" * 70)
    df_results = optimizer.get_results_dataframe()
    for i, (idx, row) in enumerate(df_results.head(5).iterrows(), 1):
        br = row.get('birth_rate', '?')
        mr = row.get('mortality_rate', '?')
        print(f"{i}. Score: {row['score']:8.4f} | Birth_rate: {br:.4f} | Mortality_rate: {mr:.6f}")
    print()
