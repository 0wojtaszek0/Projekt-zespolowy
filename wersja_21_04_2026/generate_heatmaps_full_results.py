"""
Generate heatmaps from full simulation results (50k agents, 50 years)
"""
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

# Load results
with open('gridsearch_results_full_50k_50y.json', 'r') as f:
    results_full = json.load(f)

# Create DataFrame
df = pd.DataFrame(results_full)

print(f"Loaded {len(df)} combinations from full simulation")
print(f"Score range: {df['score'].min():.2f}% to {df['score'].max():.2f}%")

# Create pivot table for heatmap
pivot = df.pivot_table(
    values='score',
    index='mortality_rate',
    columns='birth_rate',
    aggfunc='first'
)

print(f"\nHeatmap shape: {pivot.shape}")
print("\nPivot table (Scores %):")
print(pivot.round(2))

# 1. INTERACTIVE HEATMAP (Plotly)
print("\n1️⃣  Creating interactive heatmap...")
fig  = go.Figure(data=go.Heatmap(
    z=pivot.values,
    x=pivot.columns,
    y=pivot.index,
    colorscale='RdYlGn',
    colorbar=dict(title='Score (%)'),
    text=pivot.values.round(2),
    texttemplate='%{text:.2f}%',
    textfont={"size": 11},
    hovertemplate='Birth Rate: %{x:.4f}<br>Mortality Rate: %{y:.6f}<br>Score: %{z:.2f}%<extra></extra>'
))

# Mark optimal point
optimal_idx = df['score'].idxmax()
optimal = df.iloc[optimal_idx]
fig.add_scatter(
    x=[optimal['birth_rate']],
    y=[optimal['mortality_rate']],
    mode='markers',
    marker=dict(size=15, color='red', symbol='star', line=dict(color='darkred', width=2)),
    name=f"Optimal: {optimal['score']:.2f}%",
    hovertext=f"BR={optimal['birth_rate']:.4f}, MR={optimal['mortality_rate']:.6f}, Score={optimal['score']:.2f}%"
)

fig.update_layout(
    title='Grid Search Heatmap: Full Simulation (50k agents, 50 years)',
    xaxis_title='Birth Rate',
    yaxis_title='Mortality Rate',
    width=900,
    height=700,
    showlegend=True
)

fig.write_html('heatmap_full_50k_50y_interactive.html')
print("   ✅ heatmap_full_50k_50y_interactive.html")

# 2. DETAILED HEATMAP WITH INTERPOLATION
print("\n2️⃣  Creating detailed heatmap with interpolation...")
from scipy.interpolate import griddata

# Create fine grid
x_fine = np.linspace(df['birth_rate'].min(), df['birth_rate'].max(), 50)
y_fine = np.linspace(df['mortality_rate'].min(), df['mortality_rate'].max(), 50)
X_fine, Y_fine = np.meshgrid(x_fine, y_fine)

# Interpolate
Z_fine = griddata(
    (df['birth_rate'], df['mortality_rate']),
    df['score'],
    (X_fine, Y_fine),
    method='cubic'
)

fig2 = go.Figure(data=go.Contour(
    x=x_fine,
    y=y_fine,
    z=Z_fine,
    colorscale='RdYlGn',
    colorbar=dict(title='Score (%)'),
    contours=dict(showlabels=True, labelfont=dict(size=10))
))

# Add original points
fig2.add_scatter(
    x=df['birth_rate'],
    y=df['mortality_rate'],
    mode='markers',
    marker=dict(size=8, color='white', symbol='circle', line=dict(color='black', width=1)),
    name='Test Points',
    hovertext=[f"BR={br:.4f}, MR={mr:.6f}, Score={sc:.2f}%" 
               for br, mr, sc in zip(df['birth_rate'], df['mortality_rate'], df['score'])],
    hoverinfo='text'
)

# Mark optimal
fig2.add_scatter(
    x=[optimal['birth_rate']],
    y=[optimal['mortality_rate']],
    mode='markers+text',
    marker=dict(size=15, color='red', symbol='star', line=dict(color='darkred', width=2)),
    text='★',
    textposition='top center',
    name=f'Optimal: {optimal["score"]:.2f}%'
)

fig2.update_layout(
    title='Grid Search Detailed (50k, 50y): Interpolated Landscape',
    xaxis_title='Birth Rate',
    yaxis_title='Mortality Rate',
    width=900,
    height=700
)

fig2.write_html('heatmap_full_50k_50y_detailed.html')
print("   ✅ heatmap_full_50k_50y_detailed.html")

# 3. RANKING TABLE
print("\n3️⃣  Creating ranking table...")
df_sorted = df.sort_values('score', ascending=False).head(10).reset_index(drop=True)

fig3 = go.Figure(data=[go.Table(
    header=dict(
        values=['Rank', 'BR', 'MR', 'Score (%)', 'Δ Pop', 'Initial', 'Final'],
        fill_color='paleturquoise',
        align='center',
        font=dict(color='black', size=12)
    ),
    cells=dict(
        values=[
            (df_sorted.index + 1).astype(str),
            df_sorted['birth_rate'].round(4),
            df_sorted['mortality_rate'].round(6),
            df_sorted['score'].round(2),
            (df_sorted['final_population'] - df_sorted['initial_population']).astype(int),
            df_sorted['initial_population'].astype(int),
            df_sorted['final_population'].astype(int)
        ],
        fill_color=['lightgray' if i % 2 else 'white' for i in range(len(df_sorted))],
        align='center',
        font=dict(size=11)
    )
)])

fig3.update_layout(
    title='Top 10 Configurations (Full Simulation: 50k agents, 50 years)',
    height=500,
    width=900
)

fig3.write_html('heatmap_full_50k_50y_ranking.html')
print("   ✅ heatmap_full_50k_50y_ranking.html")

print(f"\n✅ All visualizations created!")
print(f"\n📊 OPTIMAL CONFIGURATION:")
print(f"   Birth Rate: {optimal['birth_rate']:.4f}")
print(f"   Mortality Rate: {optimal['mortality_rate']:.6f}")
print(f"   Score: {optimal['score']:.2f}%")
print(f"   Pop: {optimal['initial_population']:,} → {optimal['final_population']:,}")
