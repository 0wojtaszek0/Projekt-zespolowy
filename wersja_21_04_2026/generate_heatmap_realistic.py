"""
Generuj mapę ciepła (heatmap) z REALISTYCZNYMI danymi grid search V2
"""
import json
import numpy as np
import plotly.graph_objects as go

# Wczytaj wyniki V2
with open('gridsearch_results_v2_20260413_152309.json') as f:
    results = json.load(f)

# Rozpakuj parametry
data = []
for r in results:
    data.append({
        'birth_rate': r['params']['birth_rate'],
        'mortality_rate': r['params']['mortality_rate'],
        'score': r['score']
    })

# Uszereguj dla pivota
birth_rates = sorted(set(d['birth_rate'] for d in data))
mortality_rates = sorted(set(d['mortality_rate'] for d in data))

# Stwórz macierz
heatmap_values = np.zeros((len(mortality_rates), len(birth_rates)))

for d in data:
    i = mortality_rates.index(d['mortality_rate'])
    j = birth_rates.index(d['birth_rate'])
    heatmap_values[i, j] = d['score']

# Znajdź optymalne
best_score = max(heatmap_values.flat)
best_idx = np.unravel_index(np.argmax(heatmap_values), heatmap_values.shape)
best_mortality = mortality_rates[best_idx[0]]
best_birth = birth_rates[best_idx[1]]

print(f"""
╔═══════════════════════════════════════════════════════════════╗
║           REALISTYCZNA MAPA CIEPŁA - GRID SEARCH V2           ║
╚═══════════════════════════════════════════════════════════════╝

📊 DANE:
  - Birth rates: {birth_rates}
  - Mortality rates: {mortality_rates}
  - Kombinacji: {len(data)}

🏆 OPTYMALNY PARAMETRY:
  - birth_rate: {best_birth:.5f}
  - mortality_rate: {best_mortality:.6f}
  - Score: {best_score:.2f}% (populacja zmiana w 10 latach)

📈 Zakres score'ów: {heatmap_values.min():.2f}% do {heatmap_values.max():.2f}%
""")

# Stwórz figurę Plotly
fig = go.Figure(data=go.Heatmap(
    z=heatmap_values,
    x=[f"{br:.5f}" for br in birth_rates],
    y=[f"{mr:.6f}" for mr in mortality_rates],
    colorscale='RdYlGn',  # Red-Yellow-Green
    colorbar={'title': 'Score (%)'},
    hovertemplate='<b>Birth Rate: %{x}</b><br>Mortality Rate: %{y}<br>Score: %{z:.2f}%<extra></extra>',
))

# Dodaj marker dla optymalnego punktu
fig.add_trace(go.Scatter(
    x=[f"{best_birth:.5f}"],
    y=[f"{best_mortality:.6f}"],
    mode='markers+text',
    marker=dict(size=20, color='red', symbol='star'),
    text=['🏆 BEST<br>+1.30%'],
    textposition='top center',
    hovertemplate='<b>⭐ OPTIMAL PARAMETERS</b><br>Birth Rate: %{x}<br>Mortality Rate: %{y}<br>Score: +1.30%<extra></extra>',
    name='Optimal'
))

fig.update_layout(
    title={
        'text': '<b>Mapa Ciepła: Wyniki Optymalizacji Demograficznej (Grid Search V2)</b><br><sub>Populacja: 1000 agentów, Test: 10 lat, Score: % zmiana populacji</sub>',
        'x': 0.5,
        'xanchor': 'center',
        'font': {'size': 16, 'color': 'black'}
    },
    xaxis_title='Birth Rate (współczynnik urodzeń)',
    yaxis_title='Mortality Rate (współczynnik śmiertelności)',
    height=600,
    width=900,
    font=dict(family='Arial, sans-serif', size=11),
    plot_bgcolor='white',
    paper_bgcolor='white',
    hovermode='closest',
    margin=dict(l=100, r=100, t=130, b=100)
)

# Dodaj siatkę
fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')

# Zapisz
output_file = 'heatmap_gridsearch_v2_realistic.html'
fig.write_html(output_file)
print(f"✅ Plik zapisany: {output_file}\n")

# Drukuj tabelę
print("\n📋 PEŁNA TABELA WYNIKÓW:\n")
print(f"{'Birth Rate':<15} │ Mortality Rate │ Score (%)")
print("─" * 50)
for d in sorted(data, key=lambda x: -x['score'])[:10]:
    print(f"{d['birth_rate']:<15.5f} │ {d['mortality_rate']:>14.6f} │ {d['score']:>9.2f}")

