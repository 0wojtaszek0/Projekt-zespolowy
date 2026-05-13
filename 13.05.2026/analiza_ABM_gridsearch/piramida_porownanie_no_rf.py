"""
Porównanie 2 piramid (BEZ risk factors) — ABM gridsearch:

  Lewy panel:  ABM OPTIMUM — FM=1.927, MM=1.009 (score = -0.88%, najbliżej 0)
  Prawy panel: DOLNY-ŚRODKOWY 3×3 — FM=1.545, MM=1.60 (score = -26.5%)

Wybór punktów oparty o `gridsearch_full_abm_no_rf_*.json` (zob. raport
w README głównego folderu, sekcja porównania proxy ↔ ABM).

NOTE: stary skrypt `piramida_porownanie_ryzyko.py` używał OPTIMUM z proxy
(FM=2.118, MM=1.127), które w ABM bez RF daje +6.93% — czyli rośnie zamiast
być stabilne. Tu używamy prawdziwego ABM optimum.
"""
import multiprocessing as mp
import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))


POPULATION_SIZE = 50_000
SIM_MONTHS = 600

POINTS = [
    {
        "label":   "ABM OPTIMUM (z gridsearch_full_abm_no_rf)",
        "fm":      1.9272727272727272,
        "mm":      1.0090909090909091,
        "note":    "score = -0.88% — najbliżej 0 w ABM bez RF",
        "color_m": "#2980b9",
        "color_f": "#e74c3c",
    },
    {
        "label":   "DOLNY-ŚRODKOWY siatki 3×3",
        "fm":      1.5454545454545454,
        "mm":      1.6,
        "note":    "wysoka MM + środkowy FM, jak w analizie z RF",
        "color_m": "#34495e",
        "color_f": "#9b59b6",
    },
]

AGE_ORDER = [f"{s}-{s+4}" for s in range(0, 90, 5)] + ["90-94", "95-99", "100+"]


def run_sim(fm: float, mm: float, seed: int = 42):
    from simulation_engine import SimulationEngine
    from disease_model import DiseaseModel
    from citizen import Citizen

    engine = SimulationEngine(disease_model=DiseaseModel(), seed=seed)
    engine.fertility_rate = fm
    engine.mortality_multiplier = mm
    engine.household_split_probability = 0.001

    engine._create_synthetic_population(POPULATION_SIZE)
    zero_rfs = {rf: 0 for rf in Citizen.DEFAULT_RISK_FACTORS}
    for c in engine.citizens.values():
        c.risk_factors = zero_rfs.copy()

    initial_pop = sum(1 for c in engine.citizens.values() if c.alive)

    engine.run(months=SIM_MONTHS)

    alive = [c for c in engine.citizens.values() if c.alive]
    final_pop = len(alive)
    score = ((final_pop - initial_pop) / initial_pop) * 100 if initial_pop else 0.0

    years = sorted(engine.yearly_stats.keys())
    pyramid = engine.yearly_stats[years[-1]]["age_pyramid"] if years else {}

    n_alive = max(len(alive), 1)
    cvd_prev = sum(1 for c in alive if c.diseases.get("CVD", 0) == 1) / n_alive * 100
    lc_prev = sum(1 for c in alive if c.diseases.get("Lung Cancer", 0) == 1) / n_alive * 100
    ages = sorted(c.age_years for c in alive)
    median_age = ages[len(ages) // 2] if ages else 0.0

    return {
        "pyramid":     pyramid,
        "score":       score,
        "final_pop":   final_pop,
        "initial_pop": initial_pop,
        "median_age":  median_age,
        "cvd_prev":    cvd_prev,
        "lc_prev":     lc_prev,
    }


def _worker(args):
    label, fm, mm, seed = args
    try:
        return (label, run_sim(fm, mm, seed), None)
    except Exception as e:
        import traceback
        return (label, None, f"{e}\n{traceback.format_exc()}")


def pyramid_bars(pyramid: dict):
    males = [pyramid.get(b, {}).get("male", 0) for b in AGE_ORDER]
    females = [pyramid.get(b, {}).get("female", 0) for b in AGE_ORDER]
    return males, females


def score_color(score: float) -> str:
    if score > 2:
        return "#c0392b"
    if score < -2:
        return "#2471a3"
    return "#27ae60"


def main():
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    print("=" * 78)
    print("PORÓWNANIE PIRAMID — ABM gridsearch (bez RF)")
    print(f"Populacja: {POPULATION_SIZE:,} | {SIM_MONTHS} mies. ({SIM_MONTHS//12} lat)")
    print("=" * 78)

    tasks = [(p["label"], p["fm"], p["mm"], 42) for p in POINTS]
    results = {}
    with ProcessPoolExecutor(max_workers=min(mp.cpu_count(), 2)) as ex:
        futures = {ex.submit(_worker, t): t for t in tasks}
        for fut in as_completed(futures):
            label, result, err = fut.result()
            if err:
                print(f"  [BŁĄD] {label}: {err.splitlines()[0]}")
            else:
                print(f"  [OK]  {label}: score={result['score']:+.2f}% pop={result['final_pop']:,}")
            results[label] = result

    print("\n" + "=" * 78)
    print("STATYSTYKI KOŃCOWE")
    print("=" * 78)
    for p in POINTS:
        r = results.get(p["label"])
        if r is None:
            continue
        print(f"\n[{p['label']}]  FM={p['fm']:.4f}  MM={p['mm']:.4f}")
        print(f"  Populacja:     {r['initial_pop']:,} → {r['final_pop']:,}  ({r['score']:+.2f}%)")
        print(f"  Mediana wieku: {r['median_age']:.1f} lat")
        print(f"  CVD prev:      {r['cvd_prev']:.2f}%   LC prev: {r['lc_prev']:.2f}%")

    # ---------- Wizualizacja ----------
    subtitles = [
        f"<b>{p['label']}</b><br>FM={p['fm']:.3f} | MM={p['mm']:.3f} | {p['note']}"
        for p in POINTS
    ]
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=subtitles,
        shared_yaxes=True,
        horizontal_spacing=0.10,
    )

    max_count = 0
    for col_idx, p in enumerate(POINTS, start=1):
        r = results.get(p["label"])
        if r is None:
            continue
        males, females = pyramid_bars(r["pyramid"])
        max_count = max(max_count, max(males + females, default=0))

        show_leg = (col_idx == 1)
        fig.add_trace(go.Bar(
            y=AGE_ORDER, x=[-m for m in males],
            name="Mężczyźni", orientation="h",
            marker_color=p["color_m"], showlegend=show_leg,
            hovertemplate="<b>%{y}</b><br>M: %{customdata}<extra></extra>",
            customdata=males,
        ), row=1, col=col_idx)
        fig.add_trace(go.Bar(
            y=AGE_ORDER, x=females,
            name="Kobiety", orientation="h",
            marker_color=p["color_f"], showlegend=show_leg,
            hovertemplate="<b>%{y}</b><br>K: %{x}<extra></extra>",
        ), row=1, col=col_idx)

        ann_text = (
            f"<b>{r['score']:+.1f}%</b>  n={r['final_pop']:,}  "
            f"<span style='color:#555'>(mediana {r['median_age']:.0f} lat)</span><br>"
            f"<sub><b>Choroby:</b> CVD {r['cvd_prev']:.2f}%  |  "
            f"LC {r['lc_prev']:.2f}%</sub><br>"
            f"<sub><b>Risk factors:</b> WYŁĄCZONE (kalibracja gridsearch ABM)</sub>"
        )
        fig.add_annotation(
            row=1, col=col_idx,
            text=ann_text,
            x=0.5, y=0.99, xref="x domain", yref="y domain",
            xanchor="center", yanchor="top", showarrow=False,
            font=dict(size=11, color=score_color(r["score"])),
            align="center",
            bgcolor="rgba(255,255,255,0.85)", bordercolor="lightgray",
            borderwidth=1, borderpad=6,
        )

    tick_step = max(50, (max_count // 100) * 20)
    tick_vals = list(range(-max_count - tick_step, max_count + tick_step + 1, tick_step))
    tick_text = [str(abs(v)) for v in tick_vals]

    fig.update_layout(
        barmode="overlay",
        title=dict(
            text=(
                "<b>Piramidy wieku — ABM optimum vs dolny-środkowy 3×3 (BEZ risk factors)</b><br>"
                f"<sub>Populacja {POPULATION_SIZE:,} × 50 lat | "
                "kalibracja zgodna z gridsearch_full_abm_no_rf</sub>"
            ),
            x=0.5, xanchor="center", font=dict(size=16),
        ),
        height=800, width=1500,
        paper_bgcolor="white",
        plot_bgcolor="white",
        legend=dict(x=0.5, y=-0.06, xanchor="center", orientation="h", font=dict(size=12)),
        font=dict(family="Arial, sans-serif", size=11),
    )

    for col_idx in (1, 2):
        axis_name = "xaxis" if col_idx == 1 else f"xaxis{col_idx}"
        fig.update_layout({axis_name: dict(
            title="Liczba osób",
            zeroline=True, zerolinecolor="black", zerolinewidth=2,
            showgrid=True, gridcolor="#eeeeee",
            tickvals=tick_vals, ticktext=tick_text,
        )})
    fig.update_yaxes(title="Grupa wiekowa", row=1, col=1)

    out = "piramida_porownanie_no_rf.html"
    fig.write_html(out)
    print(f"\n✓ Zapisano: {out}")


if __name__ == "__main__":
    mp.set_start_method("spawn", force=True)
    main()
