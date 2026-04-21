# Instrukcja Ulepszeń Projektu ABM - Versja V3

Data: Kwiecień 2026

## 🎯 Podsumowanie Ulepszeń

Projekt zawiera teraz następujące ulepszenia zgodnie z zaleceniami:

### 1. ✅ Rozszerzenie Zakresu Parametrów Gridsearch
- **Poprzednio**: 5×5 kombinacji (zakresy 0.5-2.1)
- **Teraz**: 10×10 kombinacji (zakresy 0.1-2.8)
- **Wpływ**: Dokładniejsze skan space'u parametrów, mniejszy krok między wartościami

### 2. ✅ Mapa Ciepła w Matplotlib z Kolorami 'bwr'
- **Schemat kolorów**: Blue-White-Red (Blue=minimum/lepsze, Red=maksimum/gorsze)
- **Cechy**:
  - Równomierne podziały etykiet na osiach (nie chaotyczne 0.1, 0.21, 0.34...)
  - Funkcje wpływu poszczególnych parametrów na boku
  - Zaznaczenie punktu optymalnego gwiazdką zieloną

### 3. ✅ Rysowanie Funkcji Birth Rate i Mortality Rate
- **Gdzie**: Subploty obok głównej mapy ciepła
- **Co pokazują**: Wpływ poszczególnych parametrów na score (wskaźnik wzrostu)
- **Format**: Linia średniej + pasek ±1 standard deviation

### 4. ✅ Optymalizacja: Szukanie MINIMUM
- **Poprzednio**: Szukanie maksimum wzrostu populacji
- **Teraz**: Szukanie minimum |wzrostu| → populacja stabilna
- **Wynik**: Bardziej zbalansowana populacja

### 5. ✅ Sprawdzenie: Punkt Optymalny Nie Na Brzegu
- Funkcja `check_optimum_not_at_edge()` sprawdza czy best parameters nie padają na granice gridu
- Ostrzega jeśli optimum znaleziono na min/max wartości parametru
- Sugeruje poszerzenie gridu jeśli konieczne

### 6. ✅ Mapa Ciepła dla Pełnej Skali (50k agentów, 50 lat)
- Nowy skrypt: `gridsearch_fullscale.py`
- Uwaraza: Symulacja ~5-10 minut na kombinację
- Całość: ~8-16 godzin dla 100 kombinacji
- Włącza profiling czasu wykonania

### 7. ✅ Struktura Przechowywania Agentów
**Badanie struktury danych:**
```
SimulationEngine.citizens: Dict[int, Citizen]
  - Hash table dla szybkiego lookup (O(1))
  - Zawiera zarówno żywych jak i martwych agentów
  
Alternatywne struktury analizowane w raporcie:
  - Array-based: szybsza iteracja, marnuje miejsce
  - NumPy: wektoryzacja, mniej elastyczne
  - Tagged archive: tylko żywi agenci w pamięci
```

### 8. ✅ Profiling - Funkcje Czasowe
Nowy moduł: `performance_profiler.py`
```python
from performance_profiler import PerformanceProfiler

profiler = PerformanceProfiler()
step_times = profiler.profile_simulation_step(engine, num_steps=20)
```
**Mierzy**:
- Czas każdego kroku symulacji
- Średnia, min, max
- Wzrost czasów (bottleneck detection)

### 9. ✅ Analiza Pamięci
```python
from performance_profiler import MemoryAnalyzer

# Raport pamięci
print(MemoryAnalyzer.report_memory_usage(engine))

# Analiza struktur danych
print(MemoryAnalyzer.analyze_data_structures(engine))

# Info o strukturze
from performance_profiler import print_structure_info
print_structure_info()
```

### 10. ✅ Równomierne Podziały Etykiet Osi
- Funkcja `_set_equal_ticks()` w `GridSearchImprovedV3`
- Zamiast chaotycznych etykiet typu: 0.1, 0.21, 0.34
- Generuje równomierne: 0.1, 0.5, 0.9, 1.3, 1.7, 2.1, 2.5

---

## 📁 Nowe Pliki

### 1. `grid_search_improved_v3.py`
**Klasa**: `GridSearchImprovedV3`
- Rozszerzone parametry (10×10)
- Mapa ciepła w matplotlib bwr
- Funkcje wpływu parametrów
- Sprawdzanie brzegów
- Równomierne etykiety

**Użycie**:
```bash
python grid_search_improved_v3.py
```

### 2. `gridsearch_fullscale.py`
**Klasa**: `FullScaleGridSearch`
- Pełna skala: 50k agentów, 50 lat
- Szacowane: 8-16 godzin dla 10×10 gridu
- Uwzględnia profiling czasu
- Szczegółowy raport

**Użycie** (UWAGA - czekatek!):
```bash
python gridsearch_fullscale.py
```

### 3. `performance_profiler.py`
**Klasy**:
- `PerformanceProfiler`: mierzy czas kroków
- `MemoryAnalyzer`: analizuje pamięć i struktury

**Użycie**:
```python
from performance_profiler import PerformanceProfiler, MemoryAnalyzer

# Profiling
profiler = PerformanceProfiler()
times = profiler.profile_simulation_step(engine, num_steps=10)

# Pamięć
print(MemoryAnalyzer.report_memory_usage(engine))
print(MemoryAnalyzer.analyze_data_structures(engine))
```

---

## 🚀 Jak Używać

### Szybki Test (jak dotąd)
```bash
python grid_search_improved_v3.py
# Wyjście: heatmap_gridsearch_v3_YYYYMMDD_HHMMSS.png
```

### Pełna Skala - OSTRZEŻENIE !TIME-CONSUMING!
```bash
python gridsearch_fullscale.py
# Będzie pytać o potwierdzenie ze względu na czas
# Czas: ~8-16 godzin
```

### Profiling Wydajności
```python
from performance_profiler import PerformanceProfiler
from simulation_engine import SimulationEngine
from disease_model import DiseaseModel

# Setup
disease_model = DiseaseModel()
engine = SimulationEngine(disease_model=disease_model, seed=42)
engine._create_synthetic_population(5000)

# Profile
profiler = PerformanceProfiler()
times = profiler.profile_simulation_step(engine, num_steps=20)
```

---

## 📊 Przykłady Wyjść

### Mapa Ciepła V3
- Główna mapa ciepła (10×10 grid) w kolorach bwr
- Subplot: wpływ fertility_multiplier
- Subplot: wpływ mortality_multiplier
- Zaznaczony punkt optymalny (zielona gwiazdka)
- Równomierne etykiety osi

### Pełna Skala (50k, 50 lat)
- Identyczna wizualizacja ale dla pełnej skali
- Dodtkowy raport czasu wykonania
- Ostrzeżenia o brzegach (edge detection)

---

## ⚙️ Struktura Danych

### Citizens (Agenci)
```
SimulationEngine.citizens: Dict[int, Citizen]
├── Structure: Python dict (hash table)
├── Time complexity: O(1) lookup, O(n) iteration
├── Zawiera: Obiekty Citizen z:
│   ├── id, sex, age_months
│   ├── alive (true/false)
│   ├── household_id, zone_id
│   ├── diseasesDict, risk_factors Dict
│   ├── disability_score
│   └── health_state
└── Optymalizacja: Usuń martwych na koniec roku
```

### Zalecane Optymalizacje
1. **Lazy removal**: Usuń martwych agentów z `citizens` dict co roku
2. **NumPy arrays**: Dla liczb (age, scores) użyj numpy
3. **Vectorization**: Operacje na wielu agentach naraz
4. **Archiving**: Stare dane demograficzne do JSON

---

## 📈 Metryki wydajności

### Profiling Kroków
- Wypisuje czas każdego kroku (ms)
- Średnia, min, max
- Detektuje degradację (step times rosnące)
- Ostrzega jeśli drugą połowę jest >20% wolniejsza

### Analiza Pamięci
- Całkowita pamięć procesu (RSS, VMS)
- Liczba żywych i martwych agentów
- Przybliżony rozmiar agenta
- Rekomendacje optymalizacji

---

## 🎯 Wskazówki Optymalizacji

### Dla Dużych Populacji (>100k agentów)
1. **Pule martwych agentów**: Przechowuj Dead citizens oddzielnie
2. **Vectorization**: Użyj numpy dla demofgrafi
3. **Chunking**: Przetwarzaj agentów w batch'ach
4. **Profiling**: Regularnie profilej bottlenecks

### Dla Długich Symulacji (>100 lat)
1. **Archiving**: Co 10 lat zapisz snapshot
2. **Sparsification**: Zmniejsz ilość atrybutów w pamięci
3. **Lazy evaluation**: Oblicz statystyki tylko gdy potrzebne

### Dla Gridserchu
1. **Sampling**: Zamiast pełnych 50k, testuj na 10k
2. **Early stopping**: Wskaź jeśli populacja idzie do 0
3. **Parallelization**: Uruchom kombinacje równolegle

---

## 📝 Notatki

### Kolory Heatmap
- **Blue** (#0000FF): Minimum wartości (lepsze)
- **White** (#FFFFFF): Średnia wartość
- **Red** (#FF0000): Maksimum wartości (gorsze)

### Score (optymalizacja)
- **Niska wartość** = lepsza (populacja stabilna)
- Szukamy MINIMUM |annual_growth_rate|
- Ideał: 0% (populacja się nie zmienia)

### Etykiety Osi
- Generowane równomiernie: min, min+step, min+2*step, ...
- Nie losowe: 0.1, 0.2, 0.3, 0.4, 0.5, 0.6 (nie 0.1, 0.21, 0.34)

---

## 🐛 Troubleshooting

### "Point optimum at edge"
→ Zwiększ range `param_grid` (np. 0.1-3.0 zamiast 0.5-2.1)

### "Step times increasing"
→ Prawdopodobnie memory leak, zobacz `MemoryAnalyzer.report_memory_usage()`

### "Full-scale takes too long"
→ Testuj na 10k-20k agentach zamiast 50k
→ Zmniejsz z 10×10 na 5×5 grid

---

## 📞 Pytania/Issues
- Profiler nie rekorduje czasów? → Sprawdź `engine.step()` jest wywoływane
- Score zawsze duży? → Sprawdź zakres parametrów w `param_grid`
- Memory issues? → Usuń martwych agentów: `engine.citizens = {k:v for k,v in engine.citizens.items() if v.alive}`

---

**Wersja**: 3.0 (2026-04-21)
**Status**: ✅ Gotowe do użytku
