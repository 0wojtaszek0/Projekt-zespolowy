"""
Analiza wrażliwości: jak każdy parametr wpływa na wynik
"""
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Wczytaj wyniki
with open('gridsearch_results_v2_20260413_152309.json') as f:
    results = json.load(f)

# Rozpakuj
data = []
for r in results:
    data.append({
        'birth_rate': r['params']['birth_rate'],
        'mortality_rate': r['params']['mortality_rate'],
        'score': r['score']
    })

# Grupuj po birth_rate (średni score dla każdej wartości)
br_groups = {}
for d in data:
    br = d['birth_rate']
    if br not in br_groups:
        br_groups[br] = []
    br_groups[br].append(d['score'])

br_data = sorted([(br, np.mean(scores)) for br, scores in br_groups.items()])
br_vals = [x[0] for x in br_data]
br_scores = [x[1] for x in br_data]

# Grupuj po mortality_rate
mr_groups = {}
for d in data:
    mr = d['mortality_rate']
    if mr not in mr_groups:
        mr_groups[mr] = []
    mr_groups[mr].append(d['score'])

mr_data = sorted([(mr, np.mean(scores)) for mr, scores in mr_groups.items()])
mr_vals = [x[0] for x in mr_data]
mr_scores = [x[1] for x in mr_data]

# Stwórz subploty
fig = make_subplots(
    rows=1, cols=2,
    subplot_titles=('Wrażliwość na Birth Rate', 'Wrażliwość na Mortality Rate'),
    specs=[[{'secondary_y': False}, {'secondary_y': False}]]
)

# Birth rate plot
fig.add_trace(
    go.Scatter(
        x=br_vals,
        y=br_scores,
        mode='lines+markers',
        name='Birth Rate',
        line=dict(width=3, color='#636EFA'),
        marker=dict(size=10, line=dict(width=2, color='darkblue')),
        hovertemplate='Birth Rate: %{x:.5f}<br>Średni Score: %{y:.2f}%<extra></extra>',
        fill='tozeroy',
        fillcolor='rgba(99, 110, 250, 0.3)'
    ),
    row=1, col=1
)

# Mortality rate plot
fig.add_trace(
    go.Scatter(
        x=mr_vals,
        y=mr_scores,
        mode='lines+markers',
        name='Mortality Rate',
        line=dict(width=3, color='#EF553B'),
        marker=dict(size=10, line=dict(width=2, color='darkred')),
        hovertemplate='Mortality Rate: %{x:.6f}<br>Średni Score: %{y:.2f}%<extra></extra>',
        fill='tozeroy',
        fillcolor='rgba(239, 85, 59, 0.3)'
    ),
    row=1, col=2
)

# Aktualizuj osie
fig.update_xaxes(title_text='Birth Rate (Współczynnik Urodzeń)', row=1, col=1)
fig.update_xaxes(title_text='Mortality Rate (Współczynnik Śmiertelności)', row=1, col=2)
fig.update_yaxes(title_text='Średni Score (%)', row=1, col=1)
fig.update_yaxes(title_text='Średni Score (%)', row=1, col=2)

fig.update_layout(
    title_text='<b>Analiza Wrażliwości: Wpływ Parametrów na Score</b><br><sub>Pokazuje średni score dla każdej wartości parametru</sub>',
    height=500,
    width=1200,
    hovermode='x unified',
    plot_bgcolor='rgba(240, 240, 240, 0.5)',
    paper_bgcolor='white',
    font=dict(family='Arial, sans-serif', size=11),
    showlegend=True,
    legend=dict(x=0.5, y=-0.15, xanchor='center', yanchor='top', orientation='h')
)

# Grid
fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')

output_file = 'heatmap_gridsearch_v2_sensitivity.html'
fig.write_html(output_file)
print(f"✅ Analiza wrażliwości zapisana: {output_file}")

print("""
📈 WNIOSKI Z ANALIZY WRAŻLIWOŚCI:

Birth Rate:
""")
for br, score in br_data:
    print(f"  {br:.5f}: średni score {score:+.2f}%")

print(f"""
Metabolism: Czym wyższa birth rate, tym lepszy wynik!
Wzrost z 0.01 na 0.06 → poprawa o {br_scores[-1] - br_scores[0]:.1f}%

Mortality Rate:
""")
for mr, score in mr_data:
    print(f"  {mr:.6f}: średni score {score:+.2f}%")

print(f"""
Wniosek: Czym niższa mortality rate, tym lepszy wynik!
Spadek z 0.003 na 0.0005 → poprawa o {mr_scores[0] - mr_scores[-1]:.1f}%

🎯 Optymalna kombinacja: 
  - Maksymalna birth rate (0.06)
  - Minimalna mortality rate (0.0005)
  - Wynik: +1.30% (jedyna osiągalna dodatnia wartość!)
""")

