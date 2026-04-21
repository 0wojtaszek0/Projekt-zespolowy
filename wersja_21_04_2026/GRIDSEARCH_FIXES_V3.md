# Grid Search Optimization V3 - Fixes Summary

## Data: 21 kwietnia 2026

### ✅ Problem 1: Brak podziałek na osiach heatmapy
**Problem:** W gridsearch nie było widać jakie wartości parametrów odpowiadają poszczególnym pixelom na mapie ciepła.

**Rozwiązanie:**
- Dodano funkcję `_set_ticks_with_real_values()` 
- Ticksy są teraz ustawiane we **każzywistych współrzędnych**, nie indeksach tablicy
- Wyświetlane wartości: od 0.100 do 3.500 z równomiernym rozłożeniem

```python
# WCZEŚNIEJ (źle):
ax.set_xticks([0, 2, 4, 6, 8])  # indeksy tablicy
ax.set_xticklabels(['0.100', '0.718', '1.336', ...])

# TERAZ (poprawnie):
ax.set_xticks([0.100, 0.718, 1.336, ...])  # rzeczywiste wartości
ax.set_xticklabels(['0.100', '0.718', '1.336', ...])
```

---

### ✅ Problem 2: Punkt optymalny pada na brzeg siatki
**Problem:** Optymalne parametry wypadały na brzegu (min/max) zakresu, co sugeruje że optymum jest poza siatką.

**Rozwiązanie:**
- Ulepszona funkcja `check_optimum_not_at_edge()` 
- Teraz wyświetla **szczegółowe ostrzeżenia** z sugestiami:

```
📊 Parametr: fertility_multiplier
   Zakres: [0.10000, 3.50000]
   Wartość: 0.10000 ❌ NA DOLNEJ KRAWĘDZI!
   ⚠️ OSTRZEŻENIE: Optymalny parametr na minimalnej wartości
   → Zmniejsz zakres: np. linspace(-0.40, 3.50, ...)
```

**Akcja:**
Jeśli punkt pada na brzeg, rozszerz zakresy parametrów:
```python
param_grid = {
    "fertility_multiplier": np.linspace(0.05, 4.0, 14),  # szerzej!
    "mortality_multiplier": np.linspace(0.05, 4.0, 14),  # szerzej!
}
```

---

### ✅ Problem 3: Brak wizualizacji funkcji birth_rate i mortality_rate
**Problem:** Nie było wykreśów pokazujących jak poszczególne funkcje wpływają na score.

**Rozwiązanie:**
Dodano 6 subplotów na heatmapie:

#### Subplot 1: Heatmap (główny) - mapa ciepła z rzeczywistymi podziałami
- Niebieskie = lepsze (niski score)
- Czerwone = gorsze (wysoki score)
- Zielona gwiazdka = punkt optymalny

#### Subplot 2: Fertility Parameter Impact
**Wzór:** 
$$BR(t) = 0.03 \times fertility\_multiplier$$

Pokazuje jak wzraste score wraz ze wzrostem fertility_multiplier.

#### Subplot 3: Mortality Parameter Impact
**Wzór:** 
$$MR(t) = 0.0015 \times mortality\_multiplier$$

Pokazuje jak maleje score wraz ze wzrostem mortality_multiplier.

#### Subplot 4: Fertility - Score Dependency (Scatter)
- Poszczególne punkty pokazują średni score dla każdej wartości fertility_multiplier
- Wraz z formułą: $Birth\_Rate(t) = base\_rate \times fertility\_mult$

#### Subplot 5: Mortality - Score Dependency (Scatter)
- Poszczególne punkty pokazują średni score dla każdej wartości mortality_multiplier
- Wraz z formułą: $Mortality\_Rate(t) = base\_rate \times mortality\_mult$

---

## Matematyczne Funkcje Demograficzne

### Birth Rate (Wskaźnik Narodzin)
```
BR(year) = base_rate × fertility_multiplier
         = 0.03 × fertility_multiplier
```
- **base_rate** = 0.03 (3% rocznie)
- **fertility_multiplier**: parametr optymalizacji (0.1 - 3.5)
- Liczba narodzin: `births = population × BR(year)`

### Mortality Rate (Wskaźnik Śmiertelności)
```
MR(year) = base_rate × mortality_multiplier
         = 0.0015 × mortality_multiplier
```
- **base_rate** = 0.0015 (0.15% rocznie)
- **mortality_multiplier**: parametr optymalizacji (0.1 - 3.5)
- Liczba zgonów: `deaths = population × MR(year)`

### Population Growth (Wzrost Populacji)
```
population(t+1) = population(t) + births - deaths
                = population(t) × (1 + BR - MR)
```

### Optimization Score (Cel Optymalizacji)
```
score = |((final_population - initial_population) / initial_population) × 100| / years
```
- **Szukamy MINIMUM** (score blisko 0 = stabilna populacja)
- Małe score = populacja się nie zmienia (dobre!)
- Duże score = populacja gwałtownie rośnie lub spada (złe!)

---

## Jak Korzystać

### 1. Uruchomić Grid Search
```bash
python3 grid_search_improved_v3_fixed.py
```

### 2. Sprawdzić Wyniki
```
✓ Mapa ciepła z funkcjami zapisana do: heatmap_gridsearch_v3_fixed_YYYYMMDD_HHMMSS.png
✓ Zapisano wyniki do: gridsearch_results_v3_fixed_YYYYMMDD_HHMMSS.json
```

### 3. Jeśli Punkt Pada na Brzeg
Jeśli widzisz ostrzeżenie:
```
❌ PUNKT OPTYMALNY NA BRZEGU SIATKI!
   → Zalecane działanie: Rozszerz zakresy param_grid i uruchom ponownie
```

**Rozszerz zakresy:**
```python
# Zmniejsz minimum
"fertility_multiplier": np.linspace(0.05, 3.5, 14),

# Lub zwiększ maksimum
"fertility_multiplier": np.linspace(0.1, 4.0, 14),
```

---

## Pliki Wygenerowane

1. **heatmap_gridsearch_v3_fixed_[timestamp].png**
   - Główna wizualizacja (18" × 12")
   - Heatmap + 5 subplotów z funkcjami
   - DPI: 300 (wysoka rozdzielczość)

2. **gridsearch_results_v3_fixed_[timestamp].json**
   - Wszystkie wyniki (kombinacje parametrów + score)
   - Użyteczny do dalszej analizy

---

## Porównanie: Przed vs Po

| Aspekt | Przed | Po |
|--------|-------|-----|
| **Podziałki osi** | Indeksy tablicy (0,1,2,...) | Rzeczywiste wartości (0.100, 0.409, ...) |
| **Brzeg gridu** | Brak informacji | Szczegółowe ostrzeżenia z sugestiami |
| **Wykresy funkcji** | Brak | 5 subplotów z formułami matematycznymi |
| **Wielkość figury** | 16"×12" | 18"×12" (więcej miejsca na wykresy) |
| **Kolory formul** | - | Niebieski (Fertility), Czerwony (Mortality) |

---

## Rekomendacje

1. **Sprawdzenie brzegu**: Zawsze uruchom `check_optimum_not_at_edge()` po optymalizacji
2. **Powiększanie gridu**: Jeśli optimum na brzegu, zwiększ liczbę wartości (np. 12→16)
3. **Wizualizacja**: Zawsze sprawdzaj heatmapę - wzory funkcji są teraz widoczne!
4. **Archiwizacja**: Zapisuj wyniki JSON do porównania między runami

---

**Koniec raportu | 21 kwietnia 2026**
