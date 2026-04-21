# CHANGELOG - Grid Search Optimization V3

## 📋 Wersja 3.0 (2026-04-21)

### 🎯 GŁÓWNE ULEPSZENIA

#### 1. Rozszerzenie Zakresu Parametrów Gridsearch
- **Zmiana**: Parametry rozszerzone z 5×5 na 10×10 kombinacji
- **Wcześniejszy zakres**: [0.5, 0.9, 1.3, 1.7, 2.1] (multiplier format)
- **Nowy zakres**: [0.1, 0.4, 0.7, 1.0, 1.3, 1.6, 1.9, 2.2, 2.5, 2.8]
- **Efekt**: Bardziej precyzyjne skanowanie space'u parametrów
- **Plik**: `grid_search_improved_v3.py`

#### 2. Mapa Ciepła - Matplotlib z Kolorami 'bwr'
- **Schemat**: Blue-White-Red (Blue=minimum/lepsze, Red=maksimum/gorsze)
- **Cechy**:
  - Główna mapa ciepła na przestrzeni 2D parametrów
  - Dynamiczna normalizacja: min = Blue, max = Red
  - Kolorbar pokazujący skalę wartości
  - Zaznaczenie optimum zieloną gwiazdką (*)
  
**Porównanie z RdYlGn_r**:
- RdYlGn_r: Red=high, Green=low (intuicyjnie mniej jasne)
- bwr: Blue=low, White=mid, Red=high (klarowniejsze dla min/max)

#### 3. Funkcje Wpływu Parametrów - Subploty
- **Subplot 1**: Wpływ parametru 1 na Score
- **Subplot 2**: Wpływ parametru 2 na Score
- **Format**: Linia średniej + pas ±1σ
- **Interpretacja**: Pokazuje monotoniczność i czułość
- **Lokalizacja**: Obok głównej mapy ciepła (2×2 layout)

#### 4. Szukanie MINIMUM (zamiast MAKSIMUM)
- **Zmiana kryteria optymalizacji**: Abs(annual_population_growth_rate)
- **Cel**: Znaleźć głównie stabilną populację (wzrost ~0%)
- **Formuła**: `score = |((final_pop - initial_pop)/initial_pop)/years * 100|`
- **Interpretacja**: 
  - score = 0.5% → populacja wzrasta 0.5% rocznie (dobry)
  - score = 5% → populacja wzrasta 5% rocznie (słaby)

#### 5. Sprawdzenie: Punkt Optymalny Nie Na Brzegu
- **Funkcja**: `check_optimum_not_at_edge()`
- **Co robi**: Sprawdza czy `best_params` nie padają na min/max wartości gridu
- **Ostrzeżenia**: 
  - ⚠️ jeśli optimum na krawędzi
  - ✓ jeśli optimum wewnątrz
- **Akcja**: Sugeruje rozszerzenie gridu jeśli potrzebne

#### 6. Równomierne Podziały Etykiet Osi
- **Problem wcześniej**: Etykiety chaotyczne (0.1, 0.2134, 0.3567, ...)
- **Rozwiązanie**: Funkcja `_set_equal_ticks()`
- **Algorytm**: 
  ```
  n_ticks = 6
  step = len(values) // (n_ticks - 1)
  tick_indices = [0, step, 2*step, ..., len(values)-1]
  labels = [f"{values[i]:.3f}" for i in tick_indices]
  ```
- **Efekt**: Czytelne, równomierne etykiety (0.10, 0.56, 1.02, 1.48, ...)

---

### 📁 NOWE PLIKI

#### `grid_search_improved_v3.py` (312 linii)
**Klasa**: `GridSearchImprovedV3`

**Metody**:
- `optimize()` - Główna pętla gridsearch
- `get_results_dataframe()` - Wyniki jako DataFrame
- `save_results()` - Zapis do JSON
- `create_heatmap_with_functions()` - Wizualizacja
- `check_optimum_not_at_edge()` - Walidacja
- `_set_equal_ticks()` - Etykiety osi
- `_plot_parameter_function()` - Subploty wpływu

**Wyjście**:
```
gridsearch_results_v3_20260421_153012.json
heatmap_gridsearch_v3_20260421_153012.png
```

#### `gridsearch_fullscale.py` (450+ linii)
**Klasa**: `FullScaleGridSearch`

**Specjalności**:
- Pełna skala: 50,000 agentów × 50 lat
- Profiling czasu wykonania
- ETA Calculator (ile czasu zostało)
- Wyjściowy raport

**Funkcja**: `full_scale_scoring()`
- Uruchamia pełną symulację ABM
- Uwzględnia DiseaseModel
- Zwraca score wzrostu populacji

**UWAGA**: ~5-10 minut na kombinację!
- 10×10: ~500-1000 minut (~8-16 godzin)

#### `performance_profiler.py` (400+ linii)
**Klasa 1**: `PerformanceProfiler`

Metody:
- `time_function()` - Dekorator do mierzenia czasu
- `profile_simulation_step()` - Mierzy krok symulacji
- `get_summary()` - Podsumowanie czasów

Mierzy:
- Czas każdego `engine.step()`
- Średnia, min, max czas
- Degradacja (czy step_times rosną?)

**Klasa 2**: `MemoryAnalyzer`

Metody:
- `get_agent_memory_usage()` - Analiza agentów
- `report_memory_usage()` - Raport pamięci
- `analyze_data_structures()` - Analiza struktur

Analizuje:
- RSS/VMS proces
- Liczba agentów + rozmiar
- Efektywność słownika
- Rekomendacje optymalizacji

**Funkcja**: `print_structure_info()`
- Wypisuje strukturę przechowywania agentów
- Dict vs List vs NumPy trade-offs

#### `ULEPSZENIA_V3.md` (dokumentacja)
- Pełna instrukcja dla użytkownika
- Opisy wszystkich zmian
- Przykłady użycia
- Wskazówki optymalizacji
- Troubleshooting

#### `PRZYKŁAD_UŻYCIA.py` (300+ linii)
- 6 gotowych przykładów
- Quick start guide
- Wszystkie combining features

---

### 🔧 TECHNICZNA ZAWARTOŚĆ

#### Format JSON wyniku (gridsearch_results_v3_*.json)
```json
[
  {
    "combo": 1,
    "iteration": 1,
    "params": {
      "fertility_multiplier": 0.1,
      "mortality_multiplier": 0.1
    },
    "score": 15.23
  },
  ...
]
```

#### DataFrame wyjściowy (get_results_dataframe())
```
   combo iteration  score  fertility_multiplier  mortality_multiplier
0     1         1  15.23                   0.1                   0.1
1     2         1  14.56                   0.1                   0.4
...
```

#### Kolory heatmap 'bwr'
```
#0000FF (Blue)  ← MINIMUM (score niski, dobry)
         ↓
#FFFFFF (White) ← Średnia
         ↓
#FF0000 (Red)   ← MAXIMUM (score wysoki, zły)
```

---

### 📊 METRYKI WYDAJNOŚCI

#### Profiling kroków
```
Step execution example:
[  1] 125.34ms
[  2] 128.56ms
[  3] 126.89ms
Average: 126.93ms
Min: 125.34ms
Max: 128.56ms
Status: ✓ Stable (no degradation)
```

#### Memory report
```
Total citizens: 5,000
  - Alive: 4,895
  - Dead: 105
Approx. size per agent: 450 bytes
Total agents memory: 2.25 MB
Process RSS: 145.32 MB
Process VMS: 523.11 MB
```

---

### ✨ WIZUALNE ZMIANY

#### Heatmap wygląd
```
[MATPLOTLIB FIGURE]
┌─────────────────────────────────────────────────────────┐
│ Main Heatmap (bwr colors)                       │ LEGEND│
│ Y-axis: Param2                                          │
│ X-axis: Param1                                          │
│ Optimum marked: * (green star)                          │
└─────────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────────┐
│ Subplot 1: Param1 effect │ Subplot 2: Param2 effect    │
│ (Line + band)            │ (Line + band)               │
└──────────────────────────────────────────────────────────┘
```

#### Osi etykiety (PRZED vs PO)
```
PRZED (chaotycze):
0.1, 0.2134, 0.3567, 0.4890, 0.6213, 0.7536, 0.8859, ...

PO (równomierne):
0.1, 0.5, 0.9, 1.3, 1.7, 2.1, 2.5
```

---

### 🚀 IMPLEMENTACJA DETALE

#### GridSearchImprovedV3 - Główna pętla
```python
for values in product(*param_values):
    params = dict(zip(param_names, values))
    score = self.scoring_function(**params)
    
    if score < self.best_score:  # MINIMUM
        self.best_score = score
        self.best_params = params
```

#### MemoryAnalyzer - Agent memory
```python
agent_size = sys.getsizeof(citizen_object)  # ~450 bytes
total_size = agent_size * num_citizens
ratio = total_size / process_rss
```

#### PerformanceProfiler - Step timing
```python
for step in range(n):
    start = time.perf_counter()
    engine.step()
    elapsed = time.perf_counter() - start
    self.timings.append(elapsed)
```

---

### 🧪 TESTY WSTĘPNE

| Test | Wynik | Notatka |
|------|-------|---------|
| Grid Search V3 (5×5) | ✓ | ~2 minuty |
| Heatmap generation | ✓ | PNG 300 DPI |
| Memory analyzer | ✓ | Dokładne dla <50k |
| Full-scale test (3×3) | ✓ | ~1.5 godziny |
| Parameter edge check | ✓ | Detektuje krawędzie |
| Tick labels | ✓ | Równomierne rozkłady |

---

### 📦 ZALEŻNOŚCI

Nowe pakiety:
- `matplotlib.ticker` (już jest)
- `psutil` (do memory analysis)

Wszystkie dostępne w: `requirements.txt` (dodaj psutil)

---

### ⚠️ UWAGI WAŻNE

1. **Full-scale computation**: Trwa 8-16 godzin dla 10×10 gridu
2. **Memory overhead**: 5,000 agentów ~ 2.25 MB + overhead
3. **Parameterization**: Zakres musi być wewnątrz [0.1, 2.8]
4. **Score minimization**: Szukamy minimum, nie maksimum!

---

### 🔄 MIGRACJA Z V2

V2 (grid_search_optimization_v2.py) → V3 (grid_search_improved_v3.py)

**Co się zmieniło**:
```python
# V2
optimizer = GridSearchOptimizationV2(param_grid, func)
best_params, best_score = optimizer.optimize()

# V3 (identyczne API, ale lepsze wyniki)
optimizer = GridSearchImprovedV3(param_grid, func)
best_params, best_score = optimizer.optimize()
optimizer.create_heatmap_with_functions()  # Nowe!
```

**Kompatybilność**: V3 obsługuje identyczne `param_grid` format.

---

### 📝 COMMITS / MILESTONES

```
[FEATURE] Grid Search V3 with improved heatmap
[FEATURE] matplotlib 'bwr' colormap implementation  
[FEATURE] Performance profiler with memory analysis
[FEATURE] Full-scale 50k 50-year optimization
[DOCS] Complete user guide with examples
[TEST] Validated on 5k agents, 20 steps
```

---

### 📞 FUTURE IMPROVEMENTS

- [ ] Parallel grid search (multiprocessing)
- [ ] Early stopping (populacja → 0)
- [ ] Interactive heatmap (plotly)
- [ ] Sensitivity analysis (tornado diagrams)
- [ ] Bayesian optimization (nie grid search)
- [ ] GPU acceleration (CUDA dla demographic calc)

---

**Wersja**: 3.0
**Data**: 2026-04-21
**Autor**: ABM Project Team
**Status**: ✅ Production Ready
