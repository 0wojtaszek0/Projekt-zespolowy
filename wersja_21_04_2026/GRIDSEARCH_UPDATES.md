# GridSearch Updates - 4D Visualization

## Zmiany wprowadzone (Changes Made)

Na podstawie feedback'u z wiadomości projektowych:
- Przejście z 2D na 4D analizę grid searcha
- Nowa wizualizacja: multipanelowe heatmapy pokazujące zależności w przestrzeni 4D

## Struktura wizualizacji 4D

```
Każda heatmapa (panel): 
  X-axis: mortality_multiplier (0.5, 1.0, 1.5, 2.0)
  Y-axis: fertility_multiplier (0.5, 1.0, 1.5, 2.0)
  
Organnizacja paneli w siatkę:
  Rows: birth_rate_factor (0.8, 1.0, 1.2) - 3 scenariusze urodzeniowości
  Columns: death_rate_factor (0.7, 1.0, 1.3) - 3 scenariusze śmiertelności
  
Wynik: 3×3 = 9 heatmap pokazujących zależności Z(fertility, mortality, birth_rate, death_rate)
```

## Parametry

### Wymiary głównych heatmap (osie X, Y każdej heatmapy):
- **fertility_multiplier**: [0.5, 1.0, 1.5, 2.0]
  - Mnożnik dla współczynników płodności zależnych od wieku
  - 4 poziomy
  
- **mortality_multiplier**: [0.5, 1.0, 1.5, 2.0]  
  - Mnożnik dla współczynników śmiertelności zależnych od wieku
  - 4 poziomy

### Wymiary siatki paneli (rzędy, kolumny):
- **birth_rate_factor**: [0.8, 1.0, 1.2]
  - Skalowanie bazowej tabeli współczynników płodności
  - Reprezentuje różne scenariusze populacyjne
  - 3 poziomy (rzędy)
  
- **death_rate_factor**: [0.7, 1.0, 1.3]
  - Skalowanie bazowej tabeli współczynników śmiertelności  
  - Reprezentuje różne scenariuszy populacyjne
  - 3 poziomy (kolumny)

## Liczba kombinacji
- Razem: 4 × 4 × 3 × 3 = **144 kombinacji** do testowania

## Pliki zmienione

### 1. `heatmap_gridsearch.py` - Główny plik wizualizacji
**Nowe funkcje:**
- `create_4d_heatmaps()` - Tworzy multipanelową wizualizację 4D
- Ulepszony `create_parameter_grid()` - 4D zamiast 2D
- Ulepszony `simulation_scoring_function()` - obsługuje 4 parametry

**Zastosowane techniki:**
- `make_subplots()` z plotly do siatki heatmap
- Wspólna skala kolorów (zmin, zmax) dla wszystkich paneli
- Etykiety rzędów na lewej stronie (parametr birth_rate_factor)
- Etykiety kolumn na górze (parametr death_rate_factor)

**Wyjścia:**
- `heatmap_gridsearch_4d.html` - 4D wizualizacja (nowa)
- `heatmap_gridsearch_2d.html` - 2D wizualizacja dla referencji

### 2. `grid_search_optimization.py` - Grid search engine
**Zmiany:**
- Zaktualizowana funkcja scoring'u do obsługi 4 parametrów
- Nowy 4D parameter grid
- Skalowanie tabel demograficznych na podstawie birth_rate_factor i death_rate_factor

## Jak działajł demograficzne skalowanie

```python
# Przykład: birth_rate_factor = 1.2, death_rate_factor = 0.7

# Nowa tabela płodności
scaled_fertility_table = {age: rate * 1.2 for age, rate in default_table}

# Nowa tabela śmiertelności  
scaled_mortality_table = {
    age: (male_rate * 0.7, female_rate * 0.7) 
    for age, (male_rate, female_rate) in default_table
}

engine.fertility_table = scaled_fertility_table
engine.mortality_table = scaled_mortality_table
```

To reprezentuje różne bazowe warianty demograficzne populacji, na których następnie nakładane są fertility_multiplier i mortality_multiplier.

## Uruchomienie

```bash
# Pełna analiza z heatmapami
python heatmap_gridsearch.py

# Lub tylko oblieczenia bez wizualizacji
python grid_search_optimization.py
```

## Interpretacja wizualizacji 4D

1. **Porównaj kolorki pomiędzy panelami** - zobaczysz jak zmienia się wpływ fertility/mortality dla różnych scenariuszy urodzeniowości/śmiertelności

2. **Każdy panel** - pokazuje kombinację jednej wartości birth_rate_factor i jednej wartości death_rate_factor

3. **WHite dots na heatmapach** - jeśli będą, wskazują optymalne kombinacje parametrów

4. **Gradient kolorów** - zielony (pozytywny wzrost populacji) vs czerwony (ujemny wzrost)

## Następne kroki (opcjonalnie)

- Można zmienić zakres parametrów w `create_parameter_grid()`
- Można dodać więcej poziomów dla lepszej precyzji (ale wolniej)
- Można modyfikować skalowanie demograficzne w funkcji scoring'u
