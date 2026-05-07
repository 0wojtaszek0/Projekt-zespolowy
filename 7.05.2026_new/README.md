# Agent-Based Model — Demograficzna Symulacja Populacji Polski

> **Projekt zespołowy 2026** — Agent-Based Model (ABM) symulujący dynamikę demograficzną populacji polskiej przez 50 lat, oparty na rzeczywistych danych GUS Poland 2021 oraz danych z programu Białystok+.

---

## Spis treści

1. [Czym jest ten projekt?](#1-czym-jest-ten-projekt)
2. [Struktura plików](#2-struktura-plików)
3. [Architektura modelu](#3-architektura-modelu)
4. [Przechowywanie agentów](#4-przechowywanie-agentów)
5. [Klasy i komponenty](#5-klasy-i-komponenty)
6. [Silnik symulacji — jak działa?](#6-silnik-symulacji--jak-działa)
7. [Tabele demograficzne i wskaźniki CBR/CDR/TFR](#7-tabele-demograficzne)
8. [Gridsearch — optymalizacja parametrów](#8-gridsearch--optymalizacja-parametrów)
9. [Piramidy wieku](#9-piramidy-wieku)
10. [Wszystkie poprawki (bug fixes)](#10-wszystkie-poprawki-bug-fixes)
11. [Kalibracja — przed i po poprawkach](#11-kalibracja--przed-i-po-poprawkach)
12. [Flat rate vs. mnożnik tabel wiekowych](#12-flat-rate-vs-mnożnik-tabel-wiekowych)
13. [Wnioski](#13-wnioski)
14. [Przykładowe pytania i odpowiedzi](#14-przykładowe-pytania-i-odpowiedzi)
15. [Jak uruchomić?](#15-jak-uruchomić)

---

## 1. Czym jest ten projekt?

Jest to **pełna implementacja Agent-Based Model (ABM)** demografii populacji Polski. Każdy mieszkaniec jest osobnym obiektem (agentem), który:

- Starzeje się o 1 miesiąc na każdą iterację symulacji
- Może umrzeć z prawdopodobieństwem zależnym od wieku, płci, chorób i czynników ryzyka
- Może urodzić dziecko (jeśli jest kobietą w wieku 15–50 lat) z prawdopodobieństwem zależnym od wieku
- Należy do gospodarstwa domowego i strefy geograficznej
- Posiada choroby (CVD, Lung Cancer, Hypercholesterolemia) i czynniki ryzyka (palenie, otyłość, alkohol)

Model symuluje **50 000 agentów przez 50 lat (600 miesięcy)** używając danych z Tablic Trwania Życia GUS Poland 2021.

**Dlaczego ABM, a nie makromodel?**  
ABM pozwala na heterogeniczność — każdy agent ma własny wiek, płeć, choroby i historię. Można dokładnie śledzić piramidy wiekowe, wielochorobowość i nierówności zdrowotne w sposób niemożliwy w agregowanych modelach ODE/PDE.

---

## 2. Struktura plików

```
ABM - poprawiony gridsearch/
│
├── simulation_engine.py              # Główny silnik ABM — serce projektu
├── citizen.py                        # Klasa agenta (Citizen)
├── household.py                      # Klasa gospodarstwa domowego
├── zone.py                           # Klasa strefy geograficznej
├── disease_model.py                  # Model chorób i czynników ryzyka
├── main.py                           # Uruchamia jedną symulację, generuje wykresy
│
├── grid_search_improved_v3_fixed.py  # Analityczny gridsearch + heatmap PNG (szybki)
├── gridsearch_age_pyramids_analysis.py  # Gridsearch ABM + piramidy HTML (wolny, równoległy)
├── comparison_flatrate_vs_multiplier.py # Porównanie podejść flat-rate vs mnożnik
│
├── piramidy_gridsearch_siatka.html   # Siatka 3×3 piramid z gridsearch
├── piramidy_diagonale_gridsearch.html  # Profile wzdłuż 3 diagonali gridsearch
├── comparison_flatrate_vs_multiplier.html  # Porównanie obu podejść (2×3 piramidy)
├── heatmap_gridsearch_v3_fixed_*.png  # Analityczna mapa ciepła (PNG)
├── gridsearch_results_v3_fixed_*.json # Wyniki gridsearch (JSON)
│
└── README.md                         # Ten plik
```

---

## 3. Architektura modelu

```
┌─────────────────────────────────────────────────────────────┐
│                     SimulationEngine                        │
│                                                             │
│  citizens: Dict[int, Citizen]   ←── główna populacja       │
│  households: Dict[int, Household]                           │
│  zones: Dict[int, Zone]                                     │
│  yearly_stats: Dict[int, Dict]  ←── statystyki roczne      │
│                                                             │
│  ┌────────┐  ┌───────────┐  ┌──────┐  ┌─────────────────┐ │
│  │Citizen │  │ Household │  │ Zone │  │  DiseaseModel   │ │
│  │        │  │           │  │      │  │  - CVD          │ │
│  │age     │  │members[]  │  │zone_id│  │  - LungCancer  │ │
│  │sex     │  │zone_id    │  │air_q  │  │  - Hyperchol.  │ │
│  │alive   │  │           │  │       │  │                 │ │
│  │diseases│  │           │  │       │  │                 │ │
│  └────────┘  └───────────┘  └──────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Pętla symulacji (co miesiąc)

```
for month in range(600):           # 50 lat × 12 miesięcy
    1. age_all()                   # każdy agent: age_months += 1
    2. handle_deaths()             # losowe zgony wg tabeli śmiertelności
    3. handle_births()             # losowe narodziny wg tabeli płodności
    4. handle_household_splits()   # dorośli 25+ opuszczają domy
    5. update_health_states()      # progresja chorób
    6. if month % 12 == 0:
           collect_yearly_stats()  # piramida wieku, populacja, itp.
```

---

## 4. Przechowywanie agentów

### Struktura danych: `Dict[int, Citizen]`

```python
self.citizens: Dict[int, Citizen] = {}
# Przykład:
# {
#   0: Citizen(sex="male",  age_months=384, alive=True,  ...),
#   1: Citizen(sex="female",age_months=252, alive=True,  ...),
#   2: Citizen(sex="female",age_months=816, alive=False, ...),  ← martwy, ale zostaje
#   ...
# }
```

**Dlaczego słownik, a nie lista?**

| Kryterium | `Dict[int, Citizen]` | `List[Citizen]` |
|-----------|----------------------|-----------------|
| Lookup po ID | O(1) | O(n) |
| Usunięcie martwych | Nie trzeba (flaga `alive`) | Drogie przesunięcia |
| Iteracja po żywych | `if c.alive` | Analogicznie |
| Nowe narodziny | `citizens[newborn.id] = newborn` | `append()` |
| Stabilność referencji | Stałe ID przez całe życie | Indeksy przesuwają się |

**Kluczowy szczegół — martwi agenci NIE są usuwani ze słownika.** Mają flagę `alive = False`. Dzięki temu:
- Household może sprawdzić czy agent nadal żyje bez `KeyError`
- Statystyki retrospektywne są możliwe
- Unika się kosztownej przebudowy słownika w trakcie symulacji

**Unikalny ID agenta** jest generowany przez zmienną klasową `Citizen._next_id` i nigdy się nie powtarza (nawet po śmierci agenta).

---

## 5. Klasy i komponenty

### `Citizen` — agent populacji

```python
class Citizen:
    id: int               # unikalny, auto-inkrementowany
    sex: str              # "male" lub "female"
    age_months: int       # wiek w miesiącach (nie latach!)
    alive: bool           # True/False
    household_id: int     # przynależność do gospodarstwa
    zone_id: int          # strefa geograficzna (1–4)
    diseases: Dict[str, int]     # {"CVD": 0, "LungCancer": 1, ...}
    disability_score: float      # suma wag chorób (0.0–1.0)
    risk_factors: Dict[str, int] # {"smoking": 0, "obesity": 1, "alcohol": 0}

    # Właściwości
    @property
    def age_years(self) -> float:
        return self.age_months / 12.0

    def num_conditions(self) -> int:     # liczba aktywnych chorób
    def compute_disability_score(...)    # aktualizuje disability_score
```

**Atrybuty czynników ryzyka** są inicjalizowane losowo przy tworzeniu agenta:
- Palenie: ~25% prevalence w populacji
- Otyłość: ~20% prevalence
- Alkohol: ~15% prevalence

### `Household` — gospodarstwo domowe

```python
class Household:
    id: int
    zone_id: int
    members: List[int]   # lista ID agentów (nie obiektów!)

    def add_member(citizen_id: int)
    def remove_member(citizen_id: int)
    def size() -> int
```

Przechowuje **ID obywateli, nie referencje** — unika cyklicznych zależności i ułatwia serializację.

### `Zone` — strefa geograficzna

Model ma 4 strefy z różnymi parametrami środowiskowymi:

| Strefa | Jakość powietrza | Dostęp do opieki | Gęstość |
|--------|-----------------|------------------|---------|
| 1      | 0.75 (wysoka)   | 0.90 (dobry)     | 4000/km² |
| 2      | 0.65 (średnia)  | 0.85             | 6000/km² |
| 3      | 0.70            | 0.80             | 5000/km² |
| 4      | 0.55 (niska)    | 0.75 (ograniczony) | 8000/km² |

W aktualnej wersji parametry środowiskowe są przechowywane, ale wpływ na śmiertelność i choroby jest minimalny — głównym motorem demograficznym są wiekowe tabele GUS.

### `DiseaseModel` — model chorób

Trzy choroby z rzeczywistymi danymi epidemiologicznymi:

| Choroba | Prevalence | Disability weight |
|---------|-----------|------------------|
| CVD (choroby sercowo-naczyniowe) | 35.0% | 0.25 |
| Lung Cancer (rak płuca) | 4.5% | 0.55 |
| Hypercholesterolemia | 25.0% | 0.08 |

```python
disability_score = Σ (disease_active × disability_weight)
# Przykład: CVD + Hyperchol. → 0.25 + 0.08 = 0.33
```

### `SimulationEngine` — główny silnik

Kluczowe parametry konfiguracyjne:

```python
engine.fertility_rate = 1.0          # mnożnik płodności (FM) — historyczna nazwa
engine.mortality_multiplier = 1.0    # mnożnik śmiertelności (MM)
engine.household_split_probability = 0.001  # 0.1%/miesiąc
```

#### Dlaczego `mortality_rate` / `fertility_rate` → `mortality_multiplier` / `fertility_multiplier`?

W pierwszej wersji modelu parametry sterujące w `SimulationEngine` nazywały się `fertility_rate` i `mortality_rate`. Z biegiem prac okazało się, że **te nazwy są mylące** — sugerują, że parametr JEST stopą demograficzną (np. CBR=8.5‰, CDR=13.5‰), w jednostce promili.

W rzeczywistości te parametry są **bezwymiarowymi mnożnikami całych tabel wiekowych**:

```python
# To, co naprawdę robi parametr "fertility_rate":
monthly_birth_prob = ASFR(wiek_kobiety) / 12  ×  fertility_rate
#                    └──────┬────────┘             └──────┬─────┘
#                    stopa wiekowa GUS              MNOŻNIK (×, nie ‰!)

# To, co naprawdę robi "mortality_multiplier":
monthly_death_prob = q_x(wiek, płeć)  ×  mortality_multiplier
#                    └──────┬──────┘     └──────┬──────────┘
#                    stopa GUS              MNOŻNIK (×)
```

**Pomyłki, które generowała stara nazwa:**

- `fertility_rate = 2.0` → ktoś czyta to jako "TFR=2.0" lub "CBR=2‰". W rzeczywistości oznacza to "wszystkie wiekowe stopy ASFR × 2.0", czyli TFR ≈ 2.56 i CBR ≈ 16.6‰.
- `mortality_rate = 0.5` → wygląda jak "0.5/1000/rok". W rzeczywistości oznacza "połowa polskiej śmiertelności w każdym wieku", czyli CDR ≈ 7.8‰.

**Dlatego w gridsearch i w dokumentacji konsekwentnie używamy nazw `fertility_multiplier` (FM) i `mortality_multiplier` (MM):**

| Parametr (nowa nazwa) | Co reprezentuje | FM/MM = 1.0 znaczy | FM/MM = 2.0 znaczy |
|----------------------|-----------------|--------------------|--------------------|
| `fertility_multiplier` | mnożnik tabeli ASFR | GUS 2021 (TFR=1.28, CBR=8.3‰) | każdy ASFR × 2 (TFR≈2.56, CBR≈16.6‰) |
| `mortality_multiplier` | mnożnik tabeli q_x | GUS 2021 (CDR=15.6‰) | każdy q_x × 2 (CDR≈31‰) |

**Korzyści ze zmiany nazewnictwa:**

1. **Jednoznaczność jednostek** — mnożnik jest bezwymiarowy (×), stopa jest w promile (‰). Niemożliwe do pomylenia.
2. **Zgodność z literaturą demograficzną** — w demografii "rate" to ścisłe pojęcie (CBR, CDR, ASFR, TFR). Słowo `_multiplier` nie sugeruje, że parametr jest stopą.
3. **Czytelne wyniki gridsearch** — `FM=1.88, MM=1.0` jest jednoznaczne (1.88× polska płodność daje stabilność). Przy starej nazwie `fertility_rate=1.88` mogło być rozumiane jako "TFR=1.88" lub "1.88‰".
4. **Spójność z koncepcją** — sekcja 12 pokazuje, że istnieje alternatywa **flat rate** (rzeczywista stopa CBR/CDR jednakowa dla wszystkich wieków, w jednostce ‰). Rozdzielenie nazw `_multiplier` (×, skaluje tabele) vs. `_rate` (‰, jedna stopa dla wszystkich) eliminuje dwuznaczność.

**Status w kodzie**: Atrybut w `SimulationEngine` nadal nazywa się `self.fertility_rate` (zachowana stara nazwa dla wstecznej kompatybilności wewnątrz silnika), ale **wszystkie skrypty i dokumentacja** używają konsekwentnie `fertility_multiplier`/`FM`. Atrybut `mortality_multiplier` został przemianowany w pełni.

Przy FM=1.0 dostajemy polskie dane GUS 2021 (TFR≈1.28). Przy FM=2.0 każda stopa płodności dla danego wieku jest podwojona.

---

## 6. Silnik symulacji — jak działa?

### Inicjalizacja populacji: `_create_synthetic_population(50000)`

Generuje 50 000 agentów z polskim rozkładem wiekowym (GUS 2021):

```python
age_distribution = {
    0:  0.094,   # 0–9:   9.4%
    10: 0.098,   # 10–19: 9.8%
    20: 0.104,   # 20–29: 10.4%
    30: 0.143,   # 30–39: 14.3%
    40: 0.135,   # 40–49: 13.5%
    50: 0.137,   # 50–59: 13.7%
    60: 0.128,   # 60–69: 12.8%
    70: 0.097,   # 70–79: 9.7%
    80: 0.051,   # 80–89: 5.1%
    90: 0.013,   # 90+:   1.3%
}
```

Dla każdego agenta losowane są: dokładny wiek w przedziale dekadowym, płeć (~51% kobiet), strefa, choroby z prevalence chorób, czynniki ryzyka.

### Zgony: `handle_deaths()`

```python
for citizen in alive_citizens:
    base_rate = _get_mortality_rate(citizen.age_years, citizen.sex)
    
    # Wpływ chorób (zredukowany po poprawkach)
    disease_mult = 1.0 + 0.02 * citizen.num_conditions()
    disease_mult += 0.04 * citizen.disability_score
    
    # Wpływ czynników ryzyka
    risk_mult = 1.0
    if smoking:    risk_mult *= 1.1   # +10%
    if obesity:    risk_mult *= 1.05  # +5%
    if alcohol:    risk_mult *= 1.1   # +10%
    
    monthly_prob = base_rate * disease_mult * risk_mult * mortality_multiplier
    
    if rng.random() < monthly_prob:
        citizen.alive = False
        household.remove_member(citizen.id)
```

### Narodziny: `handle_births()`

```python
for citizen in alive_female_citizens:
    if 15.0 <= citizen.age_years <= 50.0:
        annual_rate = _get_fertility_rate(citizen.age_years)
        monthly_prob = (annual_rate / 12.0) * fertility_rate
        
        # Redukcja przez choroby (zredukowana po poprawkach)
        disease_red = 1.0 - (0.02 * conditions + 0.04 * disability)
        disease_red = max(disease_red, 0.7)  # min. 70% bazowej stawki
        
        monthly_prob *= disease_red
        
        if rng.random() < monthly_prob:
            # Utwórz noworodka w tym samym gospodarstwie
            newborn = Citizen(sex=rng.choice(["male","female"]),
                              age_months=0, ...)
            citizens[newborn.id] = newborn
            household.add_member(newborn.id)
```

### Lookup śmiertelności: `_get_mortality_rate(age_years, sex)`

Używa **floor bracket** — znajdź najwyższy klucz tabeli ≤ wiekowi agenta:

```python
age_int = int(age_years)
bracket = available_ages[0]
for a in sorted(mortality_table.keys()):
    if a <= age_int:
        bracket = a
    else:
        break
return mortality_table[bracket][0 if sex=="male" else 1]
```

Przykład: agent w wieku 63 lat → bracket = 60 (klucz 65 jest >63, więc pomijamy). Przed poprawką używano *nearest* — agent w wieku 63 dostałby stawkę dla klucza 65, co było błędem.

### Statystyki roczne: `collect_yearly_stats()`

Co 12 miesięcy zbierane są:

```python
yearly_stats[year] = {
    "total_population": int,
    "alive_count": int,
    "births_this_year": int,
    "deaths_this_year": int,
    "age_pyramid": {
        "0-4":  {"male": int, "female": int},
        "5-9":  {"male": int, "female": int},
        ...
        "100+": {"male": int, "female": int},
    },
    "multimorbidity_count": int,
    "avg_disability_score": float,
}
```

---

## 7. Tabele demograficzne

### Tabela śmiertelności (GUS Poland 2021)

Miesięczne prawdopodobieństwa zgonu (male, female):

| Wiek | Mężczyźni (/mc) | Kobiety (/mc) | Stosunek M/K |
|------|----------------|---------------|-------------|
| 0    | 0.000373       | 0.000291      | 1.28        |
| 20   | 0.000042       | 0.000012      | 3.5 (wypadki!) |
| 40   | 0.000167       | 0.000067      | 2.5         |
| 60   | 0.001375       | 0.000583      | 2.4         |
| 65   | 0.002100       | 0.001125      | 1.9         |
| 70   | 0.003292       | 0.001833      | 1.8         |
| 75   | 0.005042       | 0.003083      | 1.6         |
| 80   | 0.007658       | 0.005375      | 1.4         |
| 85   | 0.012400       | 0.009000      | 1.4         |
| 90   | 0.018333       | 0.013750      | 1.3         |

**Ważna obserwacja**: Mężczyźni mają wyższą śmiertelność w KAŻDYM przedziale wiekowym. Nadumieralność mężczyzn jest największa w wieku 20–40 (wypadki, alkohol) i stopniowo maleje na starość.

### Tabela płodności (GUS Poland 2021, ASFR)

Roczne stopy płodności (urodzenia na kobietę w danym wieku):

| Wiek | ASFR (roczna) | /miesiąc |
|------|--------------|---------|
| 15–19 | 0.011      | 0.00092 |
| 20–24 | 0.041      | 0.00342 |
| 25–29 | 0.081      | 0.00675 (szczyt) |
| 30–34 | 0.082      | 0.00683 (szczyt) |
| 35–39 | 0.034      | 0.00283 |
| 40–44 | 0.007      | 0.00058 |
| 45–49 | 0.0003     | 0.000025 |

TFR (Total Fertility Rate) = Σ ASFR × 5 lat ≈ **1.28** ≈ polskie dane GUS 2021.

---

### Wskaźniki demograficzne — CBR, CDR, TFR

Tabele wyżej dają **stopy zależne od wieku i płci** (mortality_table[wiek][płeć], ASFR(wiek)). Na ich podstawie model wylicza **agregowane wskaźniki demograficzne**, które porównujemy z danymi GUS:

#### CBR — Crude Birth Rate (surowy współczynnik urodzeń)

CBR mierzy liczbę urodzeń żywych na 1000 mieszkańców w ciągu roku.

**Wzór ogólny:**
```
CBR = (liczba urodzeń żywych w roku / średnia populacja) × 1000   [‰]
```

**W modelu ABM:**
```python
CBR = (births_this_year / total_population) * 1000
```

**Co zawiera:**
- W liczniku — **wszystkie** urodzenia (niezależnie od wieku/płci dziecka i wieku matki)
- W mianowniku — **cała** populacja (mężczyźni, kobiety, dzieci, seniorzy)
- Jednostka — promile (‰)

**Wartości:**
- Polska 2021 (GUS): **CBR ≈ 8.5‰**
- Model po kalibracji (FM=1.0): **CBR = 8.30‰** ✓

**Ograniczenie**: CBR jest "surowy" (crude), bo nie koryguje na strukturę wiekową. Społeczeństwo z większą frakcją kobiet w wieku 20–35 lat będzie miało wyższe CBR przy tej samej skłonności do rodzenia.

#### CDR — Crude Death Rate (surowy współczynnik zgonów)

CDR mierzy liczbę zgonów na 1000 mieszkańców w ciągu roku.

**Wzór ogólny:**
```
CDR = (liczba zgonów w roku / średnia populacja) × 1000   [‰]
```

**W modelu ABM:**
```python
CDR = (deaths_this_year / total_population) * 1000
```

**Co zawiera:**
- W liczniku — **wszystkie** zgony (niezależnie od wieku, płci, przyczyny)
- W mianowniku — **cała** populacja
- Jednostka — promile (‰)

**Wartości:**
- Polska 2021 (GUS): **CDR ≈ 13.5‰**
- Model po kalibracji (MM=1.0): **CDR = 15.60‰** (lekkie zawyżenie, patrz sekcja 11)

**Ograniczenie**: Tak samo "surowy" — starzejąca się populacja ma wyższe CDR przy tej samej tabeli śmiertelności wg wieku, bo więcej osób znajduje się w przedziałach wiekowych o wysokim q_x.

#### NGR — stopa wzrostu naturalnego (Natural Growth Rate)

```
NGR = CBR − CDR    [‰/rok]
```

Po 50 latach:
```
score(50) = ((1 + NGR/1000) ^ 50 − 1) × 100%
```

- Polska 2021: NGR = 8.5 − 13.5 = **−5.0‰/rok** → naturalnie ~−22% po 50 latach
- Model (FM=MM=1.0): NGR = 8.30 − 15.60 = **−7.3‰/rok** → ~−31% (faktycznie −52% przez efekty struktury wiekowej)

#### TFR — Total Fertility Rate (współczynnik dzietności)

W przeciwieństwie do CBR (surowego), TFR uwzględnia strukturę wiekową — to suma wiekowych stóp ASFR:

```
TFR = Σ ASFR(wiek) × szerokość_przedziału    [dzieci/kobietę]
```

**Interpretacja**: średnia liczba dzieci, jaką urodziłaby kobieta w ciągu całego życia, gdyby przeszła przez wszystkie wiekowe stopy ASFR z danego roku.

- TFR = 2.1 → dokładna **zastępowalność pokoleń**
- TFR < 2.1 → populacja kurczy się (bez migracji)
- Polska 2021: **TFR = 1.26**
- Model (FM=1.0): **TFR ≈ 1.28** ✓

#### Dlaczego CBR (8.3‰) wynika z TFR (1.28)?

CBR i TFR są powiązane przez frakcję kobiet w wieku rozrodczym:

```
CBR ≈ TFR × frakcja_kobiet_15-50 / długość_okresu_rozrodczego
    ≈ 1.28 × 0.23 / 35 lat
    ≈ 0.0084  =  8.4‰
```

Czyli przy TFR=1.28, jeśli ~23% populacji to kobiety w wieku 15–50 lat, a okres rozrodczy trwa 35 lat, dostajemy CBR ≈ 8.4‰. Dokładnie wartość uzyskana w modelu ABM. **To samo równanie tłumaczy, dlaczego flat-rate fertility nie działa** (sekcja 12).

---

## 8. Gridsearch — optymalizacja parametrów

### Parametry i przestrzeń poszukiwań

```python
PARAM_GRID = {
    "fertility_multiplier":  np.linspace(0.4, 2.5, 12),  # [0.40, 0.59, ..., 2.50]
    "mortality_multiplier":  np.linspace(0.3, 1.6, 12),  # [0.30, 0.42, ..., 1.60]
}
# Łącznie: 12 × 12 = 144 kombinacje parametrów
```

### Funkcja oceny (score)

```python
score = (final_population - initial_population) / initial_population × 100
```

- `score > +2%` → populacja rośnie (czerwony na heatmapie)
- `-2% ≤ score ≤ +2%` → populacja stabilna (zielony/biały)
- `score < -2%` → populacja maleje (niebieski)

### Dwa tryby gridsearch

**1. Analityczny (szybki)** — `grid_search_improved_v3_fixed.py`

Używa matematycznego modelu proxy bez uruchamiania ABM:

```python
BASE_CBR = 0.00830   # kalibrowane z ABM (FM=MM=1.0)
BASE_CDR = 0.01560   # kalibrowane z ABM (FM=MM=1.0)

effective_cbr = BASE_CBR * fertility_multiplier
effective_cdr = BASE_CDR * mortality_multiplier
annual_net_rate = effective_cbr - effective_cdr
score = ((1 + annual_net_rate) ** 50 - 1) × 100
```

Czas działania: ~1 ms per kombinacja. Generuje heatmap PNG.

**2. Pełny ABM (wolny)** — `gridsearch_age_pyramids_analysis.py`

Uruchamia kompletną symulację dla wybranych 9–21 punktów z gridsearch. Czas: ~90 sekund per symulacja. Używa `ProcessPoolExecutor` dla równoległości.

### Wyniki gridsearch

Po poprawkach (post-fix calibration):

| FM  | MM  | Score (50 lat) | Charakter |
|-----|-----|----------------|-----------|
| 0.40 | 1.60 | -66% | Silny spadek |
| 0.40 | 0.30 | -43% | Umiarkowany spadek |
| 1.88 | 1.00 | ~0% | **Stabilny** |
| 2.50 | 1.00 | +36% | Silny wzrost |
| 2.50 | 0.30 | +122% | Bardzo silny wzrost |

**Punkt stabilności**: `FM ≈ 1.88 × MM`

Np. przy MM=0.5: FM_stable ≈ 0.94; przy MM=1.0: FM_stable ≈ 1.88; przy MM=1.5: FM_stable ≈ 2.82.

---

## 9. Piramidy wieku

### `piramidy_gridsearch_siatka.html`

Siatka 3×3 piramid dla kombinacji skrajnych i środkowych wartości gridsearch:

```
         FM_low  FM_mid  FM_high
MM_low  |  (1,1) | (1,2) | (1,3) |   ← niska śmiertelność
MM_mid  |  (2,1) | (2,2) | (2,3) |
MM_high |  (3,1) | (3,2) | (3,3) |   ← wysoka śmiertelność
```

Piramidy wizualizują kształt populacji po 50 latach:
- Silny spadek → piramida odwrócona (wąska podstawa, szeroki wiek emerytalny)
- Stabilna → prostokąt
- Silny wzrost → klasyczna piramida trójkątna

### `piramidy_diagonale_gridsearch.html`

Trzy zestawy po 4 punkty wzdłuż diagonali przestrzeni gridsearch:
- **Zestaw 1**: główna przekątna FM[i], MM[i]
- **Zestaw 2**: wyższa płodność o +2 pozycje: FM[i+2], MM[i]
- **Zestaw 3**: wyższa śmiertelność o +2 pozycje: FM[i], MM[i+2]

### `comparison_flatrate_vs_multiplier.html`

Porównanie 6 piramid: 3 mnożnikowe + 3 flat-rate, dla tych samych zamierzonych CBR/CDR (patrz sekcja 12).

---

## 10. Wszystkie poprawki (bug fixes)

### Poprawka 1: Odwrócona tabela śmiertelności kobiet (KRYTYCZNA)

**Problem**: W oryginalnej tabeli kobiety starsze (65–84 lat) miały śmiertelność **2× wyższą** niż mężczyźni w tym samym wieku. Było to dokładnie odwrotnie do rzeczywistości — w Polsce (jak wszędzie) mężczyźni umierają szybciej.

```python
# STARY kod (błędny):
DEFAULT_MORTALITY_TABLE = {
    ...
    65: (0.00110, 0.00200),  # female > male — ODWRÓCONE!
    70: (0.00175, 0.00310),
    75: (0.00280, 0.00480),
    80: (0.00420, 0.00700),
    ...
}
```

```python
# NOWY kod (poprawiony — GUS 2021):
DEFAULT_MORTALITY_TABLE = {
    ...
    65: (0.002100, 0.001125),  # male ≈ 1.9× female ✓
    70: (0.003292, 0.001833),  # male ≈ 1.8× female ✓
    75: (0.005042, 0.003083),
    80: (0.007658, 0.005375),
    ...
}
```

**Skutek błędu**: Kobiety umierały za szybko na starość → populacja kurczyła się dramatycznie → wszystkie scenariusze gridsearch pokazywały -43% do -83% po 50 latach.

---

### Poprawka 2: TFR zbyt niskie (0.68 zamiast 1.26)

**Problem**: Oryginalna tabela płodności dawała TFR ≈ 0.68, podczas gdy Polska w 2021 miała TFR ≈ 1.26. Stopy były prawie dwa razy za niskie.

```python
# STARA tabela (błędna):
DEFAULT_FERTILITY_TABLE = {
    15: 0.005, 20: 0.020, 25: 0.038,
    30: 0.040, 35: 0.016, 40: 0.003, 45: 0.0001,
}
# TFR = (0.005+0.020+0.038+0.040+0.016+0.003+0.0001) × 5 ≈ 0.61
```

```python
# NOWA tabela (GUS 2021):
DEFAULT_FERTILITY_TABLE = {
    15: 0.011, 20: 0.041, 25: 0.081,
    30: 0.082, 35: 0.034, 40: 0.007, 45: 0.0003,
}
# TFR = (0.011+0.041+0.081+0.082+0.034+0.007+0.0003) × 5 ≈ 1.28
```

---

### Poprawka 3: Rozkład wiekowy nie sumował się do 1.0

**Problem**: Wartości w oryginalnym `age_distribution` sumowały się do ~0.565, nie do 1.0. Po normalizacji (Python automatycznie normalizuje przy `choices()`), osoby 90+ stanowiły **1.77%** populacji zamiast polskich **0.54%**.

```python
# STARY kod (błędny — suma = 0.565):
age_distribution = {
    0: 0.05, 10: 0.05, 20: 0.08, 30: 0.10,
    40: 0.10, 50: 0.10, 60: 0.05, 70: 0.03,
    80: 0.02, 90: 0.01
}
# 90+ po normalizacji: 0.01/0.565 = 1.77% (za dużo!)
```

```python
# NOWY kod (GUS 2021 — suma ≈ 1.0):
age_distribution = {
    0:  0.094, 10: 0.098, 20: 0.104, 30: 0.143,
    40: 0.135, 50: 0.137, 60: 0.128, 70: 0.097,
    80: 0.051, 90: 0.013
}
# 90+ po normalizacji: 0.013/1.000 = 1.3% ✓ (Polska: ~1.3%)
```

---

### Poprawka 4: Lookup śmiertelności używał nearest zamiast floor

**Problem**: Funkcja `_get_mortality_rate()` znajdowała *najbliższy* wiek w tabeli (nearest). Agent w wieku 63 lat dostawał stawkę dla klucza `65` (odległość 2) zamiast `60` (odległość 3, ale poprawny bracket). Skutek: osoby w przedziale 60–64 miały 53% wyższą śmiertelność niż powinny.

```python
# STARY kod (błędny — nearest):
closest = min(available_ages, key=lambda a: abs(a - age_int))
```

```python
# NOWY kod (poprawny — floor bracket):
bracket = available_ages[0]
for a in available_ages:
    if a <= age_int:
        bracket = a
    else:
        break
```

---

### Poprawka 5: Zbyt silny wpływ chorób na śmiertelność

**Problem**: Mnożniki chorób i czynników ryzyka były zbyt wysokie, powodując podwójne liczenie efektów już uwzględnionych w kalibrowanych tabelach GUS.

```python
# STARY kod:
disease_multiplier = 1.0 + (0.05 * citizen.num_conditions())
disease_multiplier += 0.10 * citizen.disability_score
risk_mult *= 1.3   # palenie
risk_mult *= 1.15  # otyłość
risk_mult *= 1.25  # alkohol
```

```python
# NOWY kod (zredukowane):
disease_multiplier = 1.0 + (0.02 * citizen.num_conditions())
disease_multiplier += 0.04 * citizen.disability_score
risk_mult *= 1.1   # palenie  (+10% zamiast +30%)
risk_mult *= 1.05  # otyłość  (+5%  zamiast +15%)
risk_mult *= 1.1   # alkohol  (+10% zamiast +25%)
```

**Uzasadnienie**: Przy średnim obciążeniu populacji (0.396 chorób/osobę, disability ≈ 0.079), nowe mnożniki dają disease_multiplier ≈ 1.011, czyli ~1% nadwyżki. Tabele GUS już zawierają efekty chorób populacyjnych — nie trzeba ich liczyć podwójnie.

---

### Poprawka 6: Zbyt silna redukcja płodności przez choroby + brak podestu

**Problem**: Choroby mogły redukować płodność do zera (floor = 0.0).

```python
# STARY kod:
disease_reduction = 1.0 - (0.05 * conditions + 0.10 * disability)
disease_reduction = max(disease_reduction, 0.0)  # mogło dojść do 0!
```

```python
# NOWY kod:
disease_reduction = 1.0 - (0.02 * conditions + 0.04 * disability)
disease_reduction = max(disease_reduction, 0.7)  # min. 70% bazowej stawki
```

---

## 11. Kalibracja — przed i po poprawkach

| Metryka | Przed poprawkami | Po poprawkach | Polska 2021 |
|---------|-----------------|---------------|-------------|
| CBR (FM=1.0) | ~5.2/1000/rok | **8.30/1000/rok** | ~8.5/1000/rok |
| CDR (MM=1.0) | ~25.0/1000/rok | **15.60/1000/rok** | ~13.5/1000/rok |
| TFR (FM=1.0) | ~0.68 | **~1.28** | 1.26 |
| Score (FM=1.0, MM=1.0) | -83% po 50 latach | **-52%** | — |
| FM_stable (MM=1.0) | FM > 4.8 (poza siatką!) | **FM ≈ 1.88** (w siatce ✓) |
| Zakres score gridsearch | -83% do -5% | **-66% do +122%** | — |

Wyjaśnienie dlaczego CDR=15.6/1000 zamiast polskich 13.5/1000: Model ma nieco zawyżony CDR ponieważ tabele śmiertelności GUS dotyczą całej populacji, a w modelu domyślna śmiertelność nie koryguje w dół dla efektu "zdrowej populacji syntetycznej". To akceptowalne odchylenie — ważne jest, że FM_stable jest wewnątrz siatki parametrów.

---

## 12. Flat rate vs. mnożnik tabel wiekowych

### Dwa podejścia parametryzacji

**Podejście A (flat rate)**:
```python
# Ta sama stopa dla WSZYSTKICH wieków
monthly_birth_prob = birth_rate / 12.0    # jednakowa dla każdej kobiety 15-50
monthly_death_prob = mortality_rate / 12.0  # jednakowa dla wszystkich
```

**Podejście B (mnożnik, aktualne)**:
```python
# Stopa ZALEŻY od wieku agenta (tabela GUS)
base_rate = _get_mortality_rate(citizen.age_years, citizen.sex)
monthly_prob = base_rate * mortality_multiplier
```

### Dlaczego flat rate daje złe wyniki?

**Matematyczny dowód**:

Niech birth_rate = mortality_rate = 15.6/1000/rok (zamierzony warunek stabilności CBR=CDR).

Kobiety 15–50 lat stanowią tylko **~23%** populacji (z rozkładu GUS 2021):
```
Kobiety 15-50 = (kobiety 15-19) + ... + (kobiety 45-50)
              ≈ 50% × (9.8+10.4+14.3+13.5+13.7)% 
              ≈ 50% × 61.7% = ~30.9% populacji → ale tylko frakcja 15-50
```

Przy flat rate z birth_rate = 15.6/1000:
- Rzeczywiste urodzenia = 15.6/1000 × frakcja kobiet 15-50 × populacja
- = 15.6/1000 × 0.23 × N = **3.59/1000 × N**
- Zgony = 15.6/1000 × N

Deficyt = 3.59 - 15.6 = **-12.0/1000/rok** → po 50 latach: (1 - 0.012)^50 ≈ **-45%**!

Dla stabilności przy flat rate potrzeba: `birth_rate = mortality_rate / 0.23 ≈ 4.3 × mortality_rate`.

### Wyniki eksperymentalne (50 000 agentów, 50 lat)

| Scenariusz | Zamierzone CBR/CDR | Mnożnik (B) | Flat Rate (A) |
|------------|-------------------|-------------|---------------|
| Spadek | CBR=4.2‰, CDR=15.6‰ | -52.7% | -61.4% |
| Stabilny | CBR=15.6‰, CDR=15.6‰ | **-3.5%** ✓ | **-49.1%** ✗ |
| Wzrost | CBR=20.8‰, CDR=9.4‰ | **+41.1%** ✓ | **-27.9%** ✗ |

### Kształt piramidy — flat rate vs. mnożnik

**Flat rate** generuje **prostokątne** piramidy lub piramidy z odwróconą strukturą, ponieważ:
- Śmiertelność jednakowa dla dzieci i 90-latków (nierealistyczne)
- Brak nadwyżki starczej śmiertelności → zbyt dużo starców w populacji
- Brak nadumieralności mężczyzn → symetryczna piramida

**Mnożnik tabel GUS** generuje **realistyczne polskie piramidy**:
- Wyraźna nadumieralność mężczyzn w średnim wieku
- Rosnąca śmiertelność starczą
- Szczyt płodności 25–34 → wyraźna baza piramidy przy wysokim FM

### Wniosek metodologiczny

Podejście z mnożnikami tabel wiekowych jest **fundamentalnie lepsze** z trzech powodów:

1. **Zgodność z danymi GUS** — multiplier = 1.0 odpowiada Polsce 2021
2. **Realistyczna struktura wiekowa** — inny rozkład zgonów i urodzeń według wieku
3. **Interpretowalność** — FM=1.88 oznacza konkretną polską demografię, nie arbitralną stopę

---

## 13. Wnioski

### Wnioski demograficzne

1. **Polska demografia jest deficytowa** — przy naturalnych parametrach (FM=MM=1.0) populacja spada o ~52% przez 50 lat. Dla stabilności potrzeba FM≈1.88 przy MM=1.0, czyli prawie dwukrotnie wyższej płodności niż obecna.

2. **Asymetria wrażliwości** — model jest bardziej wrażliwy na zmiany `mortality_multiplier` niż na zmiany `fertility_multiplier` w dolnych zakresach. Przy MM=0.3 (dramatyczny spadek śmiertelności) nawet niskie FM dają stabilną populację.

3. **Kształt piramidy jest diagnostyczny** — sama liczba populacji po 50 latach mówi mało; kształt piramidy wiekowej ujawnia, czy starzejemy się (szeroka góra), kurczymy u podstawy (niska płodność), czy mamy odpowiednią strukturę.

4. **Nadumieralność mężczyzn** — widoczna wyraźnie w piramidach jako asymetria (szersza strona kobieca po 50+). W Polsce mężczyźni żyją średnio o 7.5 roku krócej niż kobiety.

### Wnioski modelarskie

5. **Kalibracja jest kluczowa** — bez poprawek model dawał biologicznie niemożliwe wyniki (wszystkie scenariusze ujemne). Trzy błędy wzmacniały się nawzajem: odwrócona tabela + za niskie TFR + za wysoka śmiertelność przez choroby.

6. **ABM vs. makromodel** — ABM pozwolił wykryć błąd w tabeli kobiecej śmiertelności, który byłby ukryty w agregowanym modelu. Widzieliśmy że kobiety 65–75 umierały w modelu szybciej niż mężczyźni, co było diagnostycznym sygnałem.

7. **Równoległość jest niezbędna** — każda symulacja ABM (50k agentów, 50 lat) trwa ~90 sekund. Bez `ProcessPoolExecutor` pełny gridsearch (144 symulacje) trwałby 3.5 godziny zamiast ~20 minut.

8. **Analityczny proxy vs. pełny ABM** — analityczny scoring (fast math, 1ms) pozwala przeglądać całą siatkę 144 punktów; pełny ABM (90s) uruchamiany jest tylko dla wybranych punktów do generowania piramid. To dobry kompromis szybkość/dokładność.

---

## 14. Przykładowe pytania i odpowiedzi

**Q1: Dlaczego używamy `Dict[int, Citizen]` zamiast `List[Citizen]`?**

Słownik daje O(1) dostęp po ID. Przy 50 000 agentów i 600 krokach miesięcznych, każdy krok wymaga wielokrotnego wyszukiwania agentów po ID (w household.members, w birth linkach itp.). Z listą byłoby O(n) = O(50 000) per lookup.

**Q2: Dlaczego martwi agenci nie są usuwani ze słownika?**

Bo household przechowuje `List[int]` — same ID. Jeśli usuniemy martwego agenta ze słownika, a jego ID zostanie w `household.members`, dostaniemy `KeyError`. Flaga `alive=False` jest bezpieczniejsza i pozwala na retrospektywne analizy.

**Q3: Co oznacza `fertility_rate = 1.88` w kontekście TFR?**

FM=1.88 × TFR_base (≈1.28) ≈ TFR=2.41, czyli blisko zastępowalności pokoleń (2.1). To wartość przy której CBR ≈ CDR i populacja jest stabilna przy MM=1.0.

**Q4: Dlaczego punkt stabilności to FM≈1.88×MM, a nie FM=MM=1.0?**

Ponieważ CDR > CBR przy domyślnych ustawieniach (15.6 vs 8.3 na 1000/rok). Czyli model startuje z polską strukturą wiekową, gdzie jest dużo seniorów (duże zgony) i mało kobiet w wieku rozrodczym (mało urodzeń). Żeby zbilansować, potrzeba podnieść płodność lub obniżyć śmiertelność.

**Q5: Dlaczego flat rate nie działa dla "stabilnego" scenariusza?**

Bo urodzenia pochodzą tylko od ~23% populacji (kobiety 15-50), a zgony dotyczą 100% populacji. Przy birth_rate = mortality_rate, efektywne urodzenia to tylko 23% zgonów → silna depopulacja. Szczegóły w sekcji 12.

**Q6: Jakie byłyby wyniki dla TFR=2.1 (zastępowalność)?**

TFR=2.1 / TFR_base(1.28) ≈ FM=1.64. Przy MM=1.0: FM=1.64 < FM_stable=1.88, więc lekki spadek (~-15% po 50 latach). Do pełnej stabilności potrzeba FM=1.88 (TFR≈2.41) bo model ma CDR > polskie dane (efekt struktury wiekowej starzejącej się populacji startowej).

**Q7: Jak interpretować heatmapę gridsearch?**

Oś X: fertility_multiplier (0.4→2.5), oś Y: mortality_multiplier (0.3→1.6). Kolor: niebieski = depopulacja, biały = stabilność, czerwony = wzrost. Linia stability (FM≈1.88×MM) biegnie diagonalnie przez mapę. Lewy górny róg (niskie FM, niskie MM) = paradoks: niska płodność + niska śmiertelność = powolny spadek.

**Q8: Dlaczego simulation_engine używa `random.Random` zamiast `numpy.random`?**

Model jest sekwencyjny per agent — każdy agent losuje niezależnie w pętli. `random.Random` z seedem zapewnia pełną reproducibility. `numpy.random` jest lepszy dla operacji wektorowych (całe tablice naraz), co nie pasuje do ABM gdzie każdy agent ma własny stan.

**Q9: Co to jest disability_score i jak wpływa na symulację?**

`disability_score = Σ (disease_active[i] × disability_weight[i])`. Przy aktywnym CVD (0.25) + Hypercholesterolemia (0.08) = 0.33. Wpływa na śmiertelność (+0.04×score) i płodność (-0.04×score, min 0.7). Przy obecnym obciążeniu populacji (~0.08 avg) efekt jest ~0.3%.

**Q10: Jak przebiega tworzenie noworodka?**

```python
newborn = Citizen(
    sex=rng.choice(["male", "female"]),  # 50/50
    age_months=0,
    household_id=mother.household_id,   # do gospodarstwa matki
    zone_id=mother.zone_id,
    diseases=dm.get_initial_diseases(),  # wszystkie 0 (brak chorób)
)
newborn.risk_factors = {rf: 0 for rf in Citizen.DEFAULT_RISK_FACTORS}
citizens[newborn.id] = newborn
household.add_member(newborn.id)
```

Noworodek dziedziczy strefę i gospodarstwo matki. Nie dziedziczy chorób (choroby zdobywają się stochastycznie w `update_health_states()`). Płeć 50/50 (uproszczenie — rzeczywisty stosunek płci at birth to ~51.5% chłopcy).

---

## 15. Jak uruchomić?

### Wymagania

```bash
pip install numpy plotly scipy pandas openpyxl
```

### Jedna symulacja z wykresami

```bash
python main.py
# Generuje: population_trends.html, piramida_wieku_animowana.html, ...
```

### Analityczny gridsearch (szybki, ~30 sekund)

```bash
python grid_search_improved_v3_fixed.py
# Generuje: heatmap_gridsearch_v3_fixed_<timestamp>.png
#           gridsearch_results_v3_fixed_<timestamp>.json
```

### Gridsearch z piramidam ABM (wolny, ~20 minut)

```bash
python gridsearch_age_pyramids_analysis.py
# Generuje: piramidy_gridsearch_siatka.html    (siatka 3×3)
#           piramidy_diagonale_gridsearch.html  (3 zestawy diagonali)
```

### Porównanie flat-rate vs. mnożnik

```bash
python comparison_flatrate_vs_multiplier.py
# Generuje: comparison_flatrate_vs_multiplier.html (2×3 piramidy)
```

### Parametry do eksperymentowania

W `gridsearch_age_pyramids_analysis.py` i `comparison_flatrate_vs_multiplier.py`:

```python
POPULATION_SIZE = 50_000   # liczba agentów
SIM_MONTHS      = 600      # 50 lat
```

W `grid_search_improved_v3_fixed.py`:

```python
param_grid = {
    "fertility_multiplier": np.linspace(0.4, 2.5, 12),  # zakres FM
    "mortality_multiplier": np.linspace(0.3, 1.6, 12),  # zakres MM
}
```

---

## Technologie

| Biblioteka | Zastosowanie |
|-----------|-------------|
| Python 3.12 | Implementacja ABM |
| NumPy | Operacje numeryczne, linspace |
| Plotly | Interaktywne wykresy HTML |
| SciPy | TwoSlopeNorm dla heatmap |
| Matplotlib | Generowanie heatmap PNG |
| concurrent.futures | Równoległe symulacje (ProcessPoolExecutor) |
| random.Random | Reproducible stochastyczność per agent |

---

## Autorzy

Projekt zespołowy — **Urban Health ABM** — Demograficzna symulacja populacji Polski  
Data: 2026 | Dane: GUS Poland 2021 Tablice Trwania Życia

---

*Model jest narzędziem badawczym. Wyniki zależą od kalibracji parametrów i uproszczonych założeń (brak migracji, stałe tabele demograficzne, uproszczony model chorób).*
