# Instrukcja Uruchamiania Projektu ABM

## Szybki Start

### 1. Przygotowanie Środowiska

```bash
# Zainstaluj wymagane pakiety
pip install -r requirements.txt
```

Wymagane pakiety:
- `pandas` - wczytywanie danych Excel
- `openpyxl` - obsługa .xlsx
- `plotly` - interaktywne wykresy
- `numpy` - operacje numeryczne
- `scipy` - funkcje statystyczne

### 2. Przygotowanie Danych (Opcjonalnie)

Program może pracować na dwa sposoby:

**Opcja A: Użycie własnych danych**
- Umieść plik `population_data.xlsx` w katalogu projektu
- Plik musi zawierać kolumny:
  - `id`, `sex` (M/F), `age`, `household_id`, `zone_id`
  - 15 kolumn chorób: Obesity, Hypercholesterolemia, Osteoarthritis, itd.

**Opcja B: Automatyczne tworzenie populacji syntetycznej** (domyślnie)
- System automatycznie generuje populację 1600 osób
- Oparte na rzeczywistych współczynnikach epidemiologicznych

### 3. Uruchomienie Symulacji

```bash
python main.py
```

Program:
1. Załaduje lub stworzy populację
2. Uruchomi symulację na 50 lat (600 miesięcy)
3. Zbierze statystyki roczne
4. Wygeneruje 4 interaktywne wykresy HTML
5. Wyświetli podsumowanie wyników

### 4. Wyniki

Po uruchomieniu zostaną stworzone pliki:

```
age_pyramid_interactive.html      # Piramida wieku ze suwakiem rocznością
population_trends.html            # Trendy: populacja, multimorbidność
households_trends.html            # Liczba gospodarstw w czasie
gender_distribution.html          # Rozkład płci
```

Otwórz je w przeglądarce, aby interaktywnie eksplorować wyniki.

## Zaawansowane Użycie

### Modyfikacja Parametrów

Edytuj plik `main.py`:

```python
# Linia ~60-62
engine.fertility_rate = 1.0                    # Domyślnie 1.0
engine.mortality_multiplier = 1.0              # Domyślnie 1.0
engine.household_split_probability = 0.001     # Domyślnie 0.001
```

### Uruchomienie Różnych Scenariuszy

```bash
python scenario_analysis.py
```

Edytuj plik `scenario_analysis.py` aby aktivować różne scenariusze:
- Wyższa płodność
- Niższa śmiertelność
- Wyższa migracja

### Testowanie

```bash
python test_abm.py
```

Uruchomi 23 testy jednostkowe weryfikujące:
- Tworzenie i działanie obywateli
- Zarządzanie gospodarstwami
- Model chorób
- Silnik symulacji

## Struktura Plików

```
Projekt zespołowy/ABM_2.0/
├── main.py                          ← Główny punkt wejścia
├── citizen.py                       ← Klasa Citizen
├── household.py                     ← Klasa Household
├── disease_model.py                 ← Klasa DiseaseModel
├── simulation_engine.py             ← Klasa SimulationEngine
├── visualization.py                 ← Klasa Visualizer
├── scenario_analysis.py             ← Analiza scenariuszy
├── test_abm.py                      ← Testy jednostkowe
├── requirements.txt                 ← Zależności
├── README.md                        ← Pełna dokumentacja
├── population_data.xlsx             ← Dane wejściowe (tworzony automatycznie)
└── [wykresy HTML po uruchomieniu]
```

## Przykładowe Wyniki

```
Year 1:   Population= 1522, Households= 414
Year 10:  Population=  983, Households= 544
Year 20:  Population=  632, Households= 642
Year 50:  Population=  229, Households= 769

Multimorbidity Cases (Year 50): 77
Average Disability Score: 0.133
```

## Informacje o Symulacji

- **Horyzont**: 50 lat (600 miesięcy)
- **Inicjalna populacja**: 1600 osób (20-80 lat)
- **Liczba chorób**: 15 dominujących
- **Statystyki**: Zbierane co 12 miesięcy
- **Wizualizacje**: 4 interaktywne wykresy Plotly

## Główne Założenia Modelu

1. **Starzenie**: +1 miesiąc każdą iterację
2. **Narodziny**: Kobiety 18-40 lat, szczyt 25-30 lat
3. **Zgony**: Exponential z wiekiem, wpływ chorób
4. **Gospodarstwa**: Dynamiczne rozbijanie (osoby 25+)
5. **Multimorbidność**: Do 15 chorób, wpływ na wszystkie zdarzenia

## Rozwiązywanie Problemów

**Problem**: Populacja szybko maleje
- Zwiększ `mortality_multiplier < 1.0`
- Zwiększ `fertility_rate > 1.0`

**Problem**: Zbyt mało zmian w gospodarstwach
- Zwiększ `household_split_probability` (np. 0.005)

**Problem**: Błąd "File not found"
- Program automatycznie stworzy populację syntetyczną
- Lub umieść `population_data.xlsx` w katalogu

## Autor / Projekt

Urban Health ABM - Projekt zespołowy 2026

---

**Następne kroki**:
1. `python main.py` - Uruchomienie symulacji
2. Otwórz `.html` pliki w przeglądarce
3. Eksploruj wyniki interaktywnie
4. Zmodyfikuj parametry w `main.py` i spróbuj ponownie
