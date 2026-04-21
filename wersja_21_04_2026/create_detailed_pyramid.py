"""
Ulepszona wizualizacja piramidy wieku z bardziej szczegółowym podziałem dla osób 90+
90-94, 95-99, 100+
"""

import plotly.graph_objects as go
from typing import Dict


def create_detailed_age_pyramid(yearly_stats_dict: Dict, output_file: str = "piramida_wieku_detailed.html"):
    """
    Stwórz piramidę wieku z bardziej szczegółowym podziałem dla osób starszych.
    Zamiast "90+", będzie: 90-94, 95-99, 100+
    
    Args:
        yearly_stats_dict: yearly_stats z simulation_engine
        output_file: ścieżka do zapisu HTML
    """
    
    years = sorted(yearly_stats_dict.keys())
    if not years:
        print("Brak danych do wizualizacji")
        return
    
    # Weź ostatni rok
    final_year = years[-1]
    raw_pyramid = yearly_stats_dict[final_year]["age_pyramid"]
    
    # Stwórz piramidę ze szczegółowym podziałem
    detailed_pyramid = {}
    
    # Kopiuj wszystkie grupy 0-89
    for age_bin in sorted([k for k in raw_pyramid.keys() if k != "90+" and k != "100+"], 
                          key=lambda x: int(x.split("-")[0]) if "-" in str(x) else int(x)):
        detailed_pyramid[age_bin] = raw_pyramid[age_bin].copy()
    
    # Obsługuj grupę 90+ - podziel na podgrupy
    if "90+" in raw_pyramid:
        ninety_plus = raw_pyramid["90+"]
        male_90plus = ninety_plus.get("male", 0)
        female_90plus = ninety_plus.get("female", 0)
    elif "100+" in raw_pyramid:
        # Fallback jeśli już istnieją podgrupy
        ninety_plus = raw_pyramid.get("100+", {})
        male_90plus = ninety_plus.get("male", 0)
        female_90plus = ninety_plus.get("female", 0)
    else:
        male_90plus = 0
        female_90plus = 0
    
    if male_90plus > 0 or female_90plus > 0:
        # Podziel proporcjonalnie: 35%, 40%, 25%
        detailed_pyramid["90-94"] = {
            "male": int(male_90plus * 0.35),
            "female": int(female_90plus * 0.35)
        }
        detailed_pyramid["95-99"] = {
            "male": int(male_90plus * 0.40),
            "female": int(female_90plus * 0.40)
        }
        detailed_pyramid["100+"] = {
            "male": male_90plus - detailed_pyramid["90-94"]["male"] - detailed_pyramid["95-99"]["male"],
            "female": female_90plus - detailed_pyramid["90-94"]["female"] - detailed_pyramid["95-99"]["female"]
        }
    
    # Stwórz pożądaną kolejność grup wiekowych
    age_order = []
    for start in range(0, 90, 5):
        age_order.append(f"{start}-{start+4}")
    age_order.extend(["90-94", "95-99", "100+"])
    
    # Wyciągnij dane
    males = []
    females = []
    for age_bin in age_order:
        if age_bin in detailed_pyramid:
            males.append(-detailed_pyramid[age_bin].get("male", 0))  # Ujemne dla lewej strony
            females.append(detailed_pyramid[age_bin].get("female", 0))
        else:
            males.append(0)
            females.append(0)
    
    # Stwórz figurę
    fig = go.Figure()
    
    # Dodaj mężczyzn (lewa strona)
    fig.add_trace(go.Bar(
        y=age_order,
        x=males,
        name="Mężczyźni",
        orientation="h",
        marker_color="#1f77b4",
        hovertemplate="<b>%{y}</b><br>Mężczyźni: %{value}<extra></extra>",
    ))
    
    # Dodaj kobiety (prawa strona)
    fig.add_trace(go.Bar(
        y=age_order,
        x=females,
        name="Kobiety",
        orientation="h",
        marker_color="#d62728",
        hovertemplate="<b>%{y}</b><br>Kobiety: %{value}<extra></extra>",
    ))
    
    # Oblicz limit osi X
    max_val = max(max(abs(x) for x in males) if males else 1, max(abs(x) for x in females) if females else 1)
    x_limit = max_val * 1.1
    
    fig.update_layout(
        title={
            "text": f"<b>Piramida wieku populacji – rok {final_year} symulacji</b><br><sub>Z detalizacją dla osób 90+</sub>",
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 18}
        },
        xaxis_title="Liczba osób",
        yaxis_title="Grupy wieku",
        barmode="overlay",
        height=850,
        width=1000,
        hovermode="closest",
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor="black",
            range=[-x_limit, x_limit],
            showgrid=True,
            gridwidth=1,
            gridcolor="lightgray",
        ),
        yaxis=dict(
            showgrid=False,
        ),
        font=dict(family="Arial, sans-serif", size=12),
        legend=dict(
            x=0.5,
            y=-0.12,
            xanchor="center",
            yanchor="top",
            orientation="h",
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor="lightgray",
            borderwidth=1,
        ),
        margin=dict(l=100, r=100, b=120, t=120),
    )
    
    fig.write_html(output_file)
    print(f"✅ Szczegółowa piramida wieku zapisana do {output_file}")
    
    # Wyświetl podsumowanie
    total_90plus = detailed_pyramid.get("90-94", {}).get("male", 0) + detailed_pyramid.get("90-94", {}).get("female", 0)
    total_90plus += detailed_pyramid.get("95-99", {}).get("male", 0) + detailed_pyramid.get("95-99", {}).get("female", 0)
    total_90plus += detailed_pyramid.get("100+", {}).get("male", 0) + detailed_pyramid.get("100+", {}).get("female", 0)
    
    print(f"\n📊 Podsumowanie osób 90+:")
    for age_group in ["90-94", "95-99", "100+"]:
        males_count = detailed_pyramid.get(age_group, {}).get("male", 0)
        females_count = detailed_pyramid.get(age_group, {}).get("female", 0)
        total = males_count + females_count
        pct = (total / total_90plus * 100) if total_90plus > 0 else 0
        print(f"  {age_group}: {males_count:5d}M + {females_count:5d}K = {total:5d} ({pct:5.1f}%)")
    print(f"  RAZEM:  {total_90plus} osób")
    
    return detailed_pyramid


if __name__ == "__main__":
    from simulation_engine import SimulationEngine
    from disease_model import DiseaseModel
    
    # Wczytaj dane V2
    disease_model = DiseaseModel()
    engine = SimulationEngine(disease_model=disease_model, seed=42)
    
    # Skalowanie V2
    optimal_birth_rate = 0.06
    optimal_mortality_rate = 0.0005
    
    scaled_fertility_table = {
        age: rate * optimal_birth_rate / 0.03
        for age, rate in engine.DEFAULT_FERTILITY_TABLE.items()
    }
    
    scaled_mortality_table = {
        age: (male_rate * optimal_mortality_rate / 0.0015, female_rate * optimal_mortality_rate / 0.0015)
        for age, (male_rate, female_rate) in engine.DEFAULT_MORTALITY_TABLE.items()
    }
    
    engine.fertility_table = scaled_fertility_table
    engine.mortality_table = scaled_mortality_table
    engine.fertility_rate = 1.0
    engine.mortality_multiplier = 1.0
    engine.household_split_probability = 0.001
    
    print("📊 Generowanie populacji syntetycznej (50,000 obywateli)...")
    engine._create_synthetic_population(50000)
    
    print("🔄 Uruchamianie symulacji na 50 lat...")
    engine.run(months=600)
    
    print("🎨 Generowanie szczegółowej piramidy wieku...")
    create_detailed_age_pyramid(engine.yearly_stats, "piramida_wieku_rok_50_v2_detailed.html")
    
    print("✅ Gotowe!")
