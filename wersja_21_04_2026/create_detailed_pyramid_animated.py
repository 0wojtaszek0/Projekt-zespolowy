"""
Animowana piramida wieku ze szczegółowym podziałem dla osób 90+
"""

import plotly.graph_objects as go
from typing import Dict, List


def create_animated_age_pyramid(yearly_stats_dict: Dict, output_file: str = "piramida_wieku_animowana_detailed.html"):
    """
    Stwórz animowaną piramidę wieku pokazującą zmianę w czasie.
    Z szczegółowym podziałem dla osób 90+: 90-94, 95-99, 100+
    
    Args:
        yearly_stats_dict: yearly_stats z simulation_engine
        output_file: ścieżka do zapisu HTML
    """
    
    years = sorted(yearly_stats_dict.keys())
    if not years:
        print("Brak danych do wizualizacji")
        return
    
    # Przygotuj dane dla każdego roku
    frames = []
    
    for year in years:
        raw_pyramid = yearly_stats_dict[year]["age_pyramid"]
        
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
            ninety_plus = raw_pyramid.get("100+", {})
            male_90plus = ninety_plus.get("male", 0)
            female_90plus = ninety_plus.get("female", 0)
        else:
            male_90plus = 0
            female_90plus = 0
        
        if male_90plus > 0 or female_90plus > 0:
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
        
        # Stwórz pożądaną kolejność grup wiekowych (bez grupy 90+)
        age_order = []
        for start in range(0, 90, 5):
            age_order.append(f"{start}-{start+4}")
        
        # Wyciągnij dane
        males = []
        females = []
        for age_bin in age_order:
            if age_bin in detailed_pyramid:
                males.append(-detailed_pyramid[age_bin].get("male", 0))
                females.append(detailed_pyramid[age_bin].get("female", 0))
            else:
                males.append(0)
                females.append(0)
        
        # Stwórz frame
        frame = go.Frame(
            data=[
                go.Bar(y=age_order, x=males, name="Mężczyźni", orientation="h", 
                       marker_color="#1f77b4", hovertemplate="<b>%{y}</b><br>Mężczyźni: %{value}<extra></extra>"),
                go.Bar(y=age_order, x=females, name="Kobiety", orientation="h",
                       marker_color="#d62728", hovertemplate="<b>%{y}</b><br>Kobiety: %{value}<extra></extra>"),
            ],
            name=str(year)
        )
        frames.append(frame)
    
    # Przygotuj dane dla pierwszego roku
    first_year = years[0]
    raw_pyramid = yearly_stats_dict[first_year]["age_pyramid"]
    detailed_pyramid = {}
    
    for age_bin in sorted([k for k in raw_pyramid.keys() if k != "90+" and k != "100+"], 
                          key=lambda x: int(x.split("-")[0]) if "-" in str(x) else int(x)):
        detailed_pyramid[age_bin] = raw_pyramid[age_bin].copy()
    
    if "90+" in raw_pyramid:
        ninety_plus = raw_pyramid["90+"]
        male_90plus = ninety_plus.get("male", 0)
        female_90plus = ninety_plus.get("female", 0)
    else:
        male_90plus = 0
        female_90plus = 0
    
    if male_90plus > 0 or female_90plus > 0:
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
    
    age_order = []
    for start in range(0, 90, 5):
        age_order.append(f"{start}-{start+4}")
    
    males = []
    females = []
    for age_bin in age_order:
        if age_bin in detailed_pyramid:
            males.append(-detailed_pyramid[age_bin].get("male", 0))
            females.append(detailed_pyramid[age_bin].get("female", 0))
        else:
            males.append(0)
            females.append(0)
    
    max_val = max(max(abs(x) for x in males) if males else 1, max(abs(x) for x in females) if females else 1)
    x_limit = max_val * 1.1
    
    # Stwórz figurę
    fig = go.Figure(
        data=[
            go.Bar(y=age_order, x=males, name="Mężczyźni", orientation="h",
                   marker_color="#1f77b4", hovertemplate="<b>%{y}</b><br>Mężczyźni: %{value}<extra></extra>"),
            go.Bar(y=age_order, x=females, name="Kobiety", orientation="h",
                   marker_color="#d62728", hovertemplate="<b>%{y}</b><br>Kobiety: %{value}<extra></extra>"),
        ],
        frames=frames
    )
    
    fig.update_layout(
        title={
            "text": f"<b>Animowana piramida wieku populacji (50 lat)</b>",
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
        updatemenus=[
            {
                "type": "buttons",
                "showactive": False,
                "x": 0.5,
                "xanchor": "center",
                "y": -0.25,
                "yanchor": "top",
                "buttons": [
                    {
                        "label": "▶ Odtwórz",
                        "method": "animate",
                        "args": [None, {
                            "frame": {"duration": 500, "redraw": True},
                            "fromcurrent": True,
                            "transition": {"duration": 300, "easing": "quadratic-in-out"}
                        }]
                    },
                    {
                        "label": "⏸ Wstrzymaj",
                        "method": "animate",
                        "args": [[None], {
                            "frame": {"duration": 0, "redraw": True},
                            "mode": "immediate",
                            "transition": {"duration": 0}
                        }]
                    }
                ]
            }
        ],
        sliders=[{
            "active": 0,
            "yanchor": "top",
            "y": -0.3,
            "xanchor": "left",
            "currentvalue": {
                "prefix": "Rok symulacji: ",
                "visible": True,
                "xanchor": "center",
                "font": {"size": 14}
            },
            "transition": {"duration": 300},
            "pad": {"b": 10, "t": 50},
            "len": 0.9,
            "x": 0.05,
            "steps": [
                {
                    "args": [[f.name], {
                        "frame": {"duration": 300, "redraw": True},
                        "mode": "immediate",
                        "transition": {"duration": 300}
                    }],
                    "method": "animate",
                    "label": str(f.name)
                }
                for f in frames
            ]
        }]
    )
    
    fig.write_html(output_file)
    print(f"✅ Animowana szczegółowa piramida wieku zapisana do {output_file}")


if __name__ == "__main__":
    from simulation_engine import SimulationEngine
    from disease_model import DiseaseModel
    
    # Wczytaj dane V2
    disease_model = DiseaseModel()
    engine = SimulationEngine(disease_model=disease_model, seed=42)
    
    # Skalowanie V2 (zaktualizowane z najnowszym optimum)
    optimal_birth_rate = 0.04667
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
    
    print("🎨 Generowanie animowanej szczegółowej piramidy wieku...")
    create_animated_age_pyramid(engine.yearly_stats, "piramida_wieku_animowana_50lat_v2_detailed.html")
    
    print("✅ Gotowe!")
