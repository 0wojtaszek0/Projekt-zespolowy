"""
Generuj SZCZEGÓŁOWĄ mapę ciepła z interpolacją i statystykami
"""
import json
import numpy as np
import plotly.graph_objects as go
from scipy.interpolate import griddata

# Wczytaj wyniki V2
with open('gridsearch_results_v2_20260413_152309.json') as f:
    results = json.load(f)

# Rozpakuj
data_points = []
for r in results:
    data_points.append([
        r['params']['birth_rate'],
        r['params']['mortality_rate'],
        r['score']
    ])

data_points = np.array(data_points)

# Interpoluj dla gładszej heatmapy
xi = np.linspace(data_points[:, 0].min(), data_points[:, 0].max(), 30)
yi = np.linspace(data_points[:, 1].min(), data_points[:, 1].max(), 30)
xi_grid, yi_grid = np.meshgrid(xi, yi)

# Interpoluj wartości
zi_smooth = griddata(
    data_points[:, :2],
    data_points[:, 2],
    (xi_grid, yi_grid),
    method='cubic'
)

# Stwórz figurę z subplotami
fig = go.Figure()

# Heatmapy
fig.add_trace(go.Heatmap(
    z=zi_smooth,
    x=xi,
    y=yi,
    colorscale='RdYlGn',
    colorbar={'title': 'Score (%)'},
    name='Interpolated',
    hovertemplate='Birth Rate: %{x:.5f}<br>Mortality Rate: %{y:.6f}<br>Score: %{z:.2f}%<extra></extra>',
))

# Dodaj oryginalne punkty
fig.add_trace(go.Scatter(
    x=data_points[:, 0],
    y=data_points[:, 1],
    mode='markers',
    marker=dict(
        size=8,
        color=data_points[:, 2],
        colorscale='RdYlGn',
        showscale=False,
        line=dict(width=1, color='black')
    ),
    text=[f'Score: {s:.2f}%' for s in data_points[:, 2]],
    hovertemplate='<b>Rzeczywisty punkt</b><br>Birth Rate: %{x:.5f}<br>Mortality Rate: %{y:.6f}<br>%{text}<extra></extra>',
    name='Grid Points',
    showlegend=True
))

# Optimal point
best_idx = np.argmax(data_points[:, 2])
best = data_points[best_idx]
fig.add_trace(go.Scatter(
    x=[best[0]],
    y=[best[1]],
    mode='markers+text',
    marker=dict(size=25, color='red', symbol='star', line=dict(width=2, color='darkred')),
    text=['🏆 OPTIMAL<br>+1.30%'],
    textposition='top center',
    textfont=dict(size=12, color='darkred'),
    hovertemplate='<b>⭐ PARAMETRY OPTYMALNE</b><br>Birth Rate: %{x:.5f}<br>Mortality Rate: %{y:.6f}<br>Score: +1.30%<extra></extra>',
    name='Optimal',
    showlegend=True
))

fig.update_layout(
    title={
        'text': '<b>Szczegółowa Mapa Ciepła: Optymalizacja Demograficzna (V2)</b><br><sub>Biały punkt = rzeczywisty test | Gwiazda = optymalny | Interpolacja sześcienna dla gładkości</sub>',
        'x': 0.5,
        'xanchor': 'center',
        'font': {'size': 15, 'color': 'black'}
    },
    xaxis_title='Birth Rate (Współczynnik Urodzeń)',
    yaxis_title='Mortality Rate (Współczynnik Śmiertelności)',
    height=700,
    width=1000,
    font=dict(family='Arial, sans-serif', size=11),
    plot_bgcolor='rgba(240, 240, 240, 0.5)',
    paper_bgcolor='white',
    hovermode='closest',
    margin=dict(l=120, r=100, t=150, b=110),
    legend=dict(x=0.02, y=0.98, bgcolor='rgba(255,255,255,0.8)', bordercolor='gray', borderwidth=1)
)

# Siatka
fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')

# Zapisz
output_file = 'heatmap_gridsearch_v2_detailed.html'
fig.write_html(output_file)
print(f"✅ Szczegółowa heatmapa zapisana: {output_file}")

# Statystyki
print(f"""
📊 STATYSTYKI OPTYMALIZACJI:

Minimalne Score: {data_points[:, 2].min():.2f}%
Maksymalne Score: {data_points[:, 2].max():.2f}%
Średnie Score: {data_points[:, 2].mean():.2f}%
Mediana Score: {np.median(data_points[:, 2]):.2f}%

🏆 TOP 5 konfiguracji:
""")

for i, idx in enumerate(np.argsort(-data_points[:, 2])[:5]):
    point = data_points[idx]
    print(f"  {i+1}. birth_rate={point[0]:.5f}, mortality_rate={point[1]:.6f} → {point[2]:+.2f}%")

