# Analiza wyników ABM gridsearch (bez risk factors)

Folder zawiera wizualizacje oparte o nowy gridsearch **`gridsearch_full_abm_no_rf.py`** (z folderu nadrzędnego), który uruchamia pełny ABM dla 144 punktów siatki 12×12, ale z wyłączonymi risk factors (wszyscy agenci mają `RF=0`).

Różnica względem analogicznych skryptów w folderze nadrzędnym (`piramida_porownanie_ryzyko.py`, `populacja_w_czasie.py`):
- Tu RFs są **wyłączone** — model Coxa działa tylko z baseline + age growth (Gompertz)
- Punkty kalibracji pochodzą z **prawdziwego ABM optimum** (FM=1.927, MM=1.009), nie z proxy (FM=2.118, MM=1.127)
- Cel: izolować efekty czysto demograficzne od epidemiologicznych

## Zawartość

| Plik | Opis | Runtime |
|------|------|---------|
| `piramidy_3x3_no_rf.py` | Siatka 3×3 piramid (9 ABM bez RF) — FM∈[0.40, 1.55, 2.50] × MM∈[0.30, 1.01, 1.60] | ~10-15 min |
| `piramida_porownanie_no_rf.py` | 2 piramidy: ABM optimum vs dolny-środkowy 3×3 | ~10 min |
| `populacja_w_czasie_no_rf.py` | Trajektorie 50 lat dla tych samych 2 punktów | ~10 min |
| `graf_ryzyko_choroby.py` | Graf RF→choroby (RF-niezależny, pokazuje macierz β z `disease_model.py`) | ~5s |

## Punkty kalibracji

| Punkt | FM | MM | ABM score (bez RF) | Charakter |
|-------|----|----|-------------------|-----------|
| **ABM OPTIMUM** | 1.927 | 1.009 | **−0.88%** | najbliżej 0 w gridsearch ABM |
| DOLNY-ŚRODKOWY 3×3 | 1.545 | 1.600 | **−26.5%** | wysokie MM, środkowe FM |

Stare optimum proxy (FM=2.118, MM=1.127) daje w ABM bez RF **+6.93%**, co potwierdza że proxy systematycznie się myli z dala od MM≈1.0.

## Jak uruchomić

```bash
cd analiza_ABM_gridsearch

# Graf RF → choroby (najszybsze, ~5s)
python graf_ryzyko_choroby.py

# Piramidy 3×3 (9 symulacji, ~10-15 min)
python piramidy_3x3_no_rf.py

# Porównanie 2 piramid (2 symulacje, ~10 min)
python piramida_porownanie_no_rf.py

# Trajektorie ludności (2 symulacje, ~10 min)
python populacja_w_czasie_no_rf.py
```

## Generowane pliki HTML

| Plik | Co pokazuje |
|------|-------------|
| `piramidy_3x3_no_rf.html` | 9 piramid w siatce 3×3 z adnotacjami score%, mediana wieku, prevalencje |
| `piramida_porownanie_no_rf.html` | 2 piramidy obok siebie z detalami |
| `populacja_w_czasie_no_rf.html` | Wykresy liniowe M/F/total 50 lat |
| `graf_ryzyko_choroby.html` | Sankey + sieć dwudzielna + heatmapa HR (7 RF × 2 choroby) |

## Źródło punktów kalibracji

`gridsearch_full_abm_no_rf_20260511_114958.json` w folderze nadrzędnym (144 wyniki ABM).
