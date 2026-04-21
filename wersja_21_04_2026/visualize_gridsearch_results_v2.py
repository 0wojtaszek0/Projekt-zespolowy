"""
Wizualizacja wyników Grid Search V2 - heatmap'y i interaktywne wykresy Plotly
birth_rate vs mortality_rate
"""

import json
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path


class GridSearchVisualizerV2:
    def __init__(self, results_file: str):
        """
        Załaduj wyniki z JSON'a
        
        Args:
            results_file: Ścieżka do pliku JSON z wynikami gridsearch'a V2
        """
        with open(results_file, 'r') as f:
            self.raw_results = json.load(f)
        
        self.results_df = pd.DataFrame([
            {
                'birth_rate': r['params']['birth_rate'],
                'mortality_rate': r['params']['mortality_rate'],
                'score': r['score']
            }
            for r in self.raw_results
        ])
        
        print(f"✓ Załadowano {len(self.results_df)} kombinacji parametrów")
        print(f"✓ Najlepszy score: {self.results_df['score'].max():.4f}")
        print(f"✓ Najgorszy score: {self.results_df['score'].min():.4f}")
    
    def create_interactive_heatmap_plotly(self, output_file: str = "heatmap_gridsearch_v2_interactive.html"):
        """
        Stwórz interaktywny heatmap w Plotly dla V2
        """
        # Pivot table dla heatmap'a
        heatmap_data = self.results_df.pivot_table(
            index='mortality_rate',
            columns='birth_rate',
            values='score'
        )
        
        # Sortuj osie
        heatmap_data = heatmap_data.sort_index(ascending=False)
        heatmap_data = heatmap_data[[float(x) for x in sorted(heatmap_data.columns)]]
        
        # Znajdź najlepszy punkt
        best_row = self.results_df.loc[self.results_df['score'].idxmax()]
        
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data.values,
            x=heatmap_data.columns,
            y=heatmap_data.index,
            colorscale='RdYlGn',
            text=np.round(heatmap_data.values, 2),
            texttemplate='%{text:.2f}',
            textfont={"size": 10},
            colorbar=dict(title="Score (%)<br>Zmiana populacji")
        ))
        
        # Dodaj marker dla najlepszego wyniku
        fig.add_trace(go.Scatter(
            x=[best_row['birth_rate']],
            y=[best_row['mortality_rate']],
            mode='markers',
            marker=dict(size=15, color='red', symbol='star', line=dict(color='darkred', width=2)),
            name=f"Best: {best_row['score']:.2f}%",
            hovertemplate=f"<b>Birth Rate:</b> %{{x:.5f}}<br><b>Mortality Rate:</b> %{{y:.5f}}<br><b>Score:</b> {best_row['score']:.2f}%<extra></extra>"
        ))
        
        fig.update_layout(
            title={
                'text': "<b>Grid Search V2 Results: Population Change (%)</b><br><sub>2 Parameters: Birth Rate vs Mortality Rate</sub>",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18}
            },
            xaxis_title="<b>Birth Rate</b>",
            yaxis_title="<b>Mortality Rate</b>",
            hovermode='closest',
            width=900,
            height=700,
            font=dict(size=12),
            paper_bgcolor='white',
            plot_bgcolor='white'
        )
        
        fig.write_html(output_file)
        print(f"✓ Zapisano mapę ciepła (Plotly): {output_file}")
    
    def create_3d_surface_plot(self, output_file: str = "heatmap_gridsearch_v2_3d.html"):
        """
        Stwórz 3D surface plot z Plotly dla V2
        """
        # Pivot table
        heatmap_data = self.results_df.pivot_table(
            index='mortality_rate',
            columns='birth_rate',
            values='score'
        )
        
        heatmap_data = heatmap_data.sort_index(ascending=False)
        heatmap_data = heatmap_data[[float(x) for x in sorted(heatmap_data.columns)]]
        
        fig = go.Figure(data=[go.Surface(
            z=heatmap_data.values,
            x=heatmap_data.columns,
            y=heatmap_data.index,
            colorscale='RdYlGn',
            colorbar=dict(title="Score (%)")
        )])
        
        fig.update_layout(
            title={
                'text': "<b>3D Surface: Population Change (Score)</b><br><sub>Birth Rate × Mortality Rate</sub>",
                'x': 0.5,
                'xanchor': 'center'
            },
            scene=dict(
                xaxis_title='Birth Rate',
                yaxis_title='Mortality Rate',
                zaxis_title='Score (%)',
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.3)
                )
            ),
            width=1000,
            height=800,
            hovermode='closest'
        )
        
        fig.write_html(output_file)
        print(f"✓ Zapisano 3D surface: {output_file}")
    
    def create_ranking_table(self, output_file: str = "gridsearch_ranking_v2.html", top_n: int = 10):
        """
        Stwórz interaktywną tabelę z top N wynikami V2
        """
        ranking = self.results_df.nlargest(top_n, 'score').reset_index(drop=True)
        ranking['Rank'] = range(1, len(ranking) + 1)
        ranking = ranking[['Rank', 'birth_rate', 'mortality_rate', 'score']]
        ranking.columns = ['Rank', 'Birth Rate', 'Mortality Rate', 'Score (%)']
        
        # Format wartości
        ranking['Birth Rate'] = ranking['Birth Rate'].apply(lambda x: f"{x:.5f}")
        ranking['Mortality Rate'] = ranking['Mortality Rate'].apply(lambda x: f"{x:.5f}")
        ranking['Score (%)'] = ranking['Score (%)'].apply(lambda x: f"{x:.2f}")
        
        # Stwórz tabelę Plotly
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=list(ranking.columns),
                fill_color='#2ca02c',
                align='center',
                font=dict(color='white', size=12, family='Arial')
            ),
            cells=dict(
                values=[ranking[col] for col in ranking.columns],
                fill_color=[
                    ['#e8f5e9' if i % 2 == 0 else 'white' for i in range(len(ranking))]
                    for _ in ranking.columns
                ],
                align='center',
                font=dict(size=11, family='Arial'),
                height=30
            )
        )])
        
        fig.update_layout(
            title={
                'text': f"<b>Top {top_n} Grid Search V2 Results</b>",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18}
            },
            height=450 + top_n * 30,
            width=700,
            margin=dict(l=50, r=50, t=100, b=50),
            paper_bgcolor='white',
            plot_bgcolor='white'
        )
        
        fig.write_html(output_file)
        print(f"✓ Zapisano ranking (Top {top_n}): {output_file}")
    
    def print_summary(self):
        """
        Wypisz podsumowanie wyników V2
        """
        print("\n" + "="*70)
        print("PODSUMOWANIE WYNIKÓW GRID SEARCH V2")
        print("="*70)
        
        best = self.results_df.loc[self.results_df['score'].idxmax()]
        worst = self.results_df.loc[self.results_df['score'].idxmin()]
        
        print(f"\n🏆 NAJLEPSZE PARAMETRY:")
        print(f"   Birth Rate: {best['birth_rate']:.5f}")
        print(f"   Mortality Rate: {best['mortality_rate']:.5f}")
        print(f"   Score (zmiana populacji): {best['score']:.2f}%")
        
        print(f"\n📊 STATYSTYKI:")
        print(f"   Średnia score: {self.results_df['score'].mean():.2f}%")
        print(f"   Mediana score: {self.results_df['score'].median():.2f}%")
        print(f"   Std dev: {self.results_df['score'].std():.2f}%")
        print(f"   Min score: {worst['score']:.2f}%")
        print(f"   Max score: {best['score']:.2f}%")
        
        print(f"\n⚠️ NAJGORSZE PARAMETRY:")
        print(f"   Birth Rate: {worst['birth_rate']:.5f}")
        print(f"   Mortality Rate: {worst['mortality_rate']:.5f}")
        print(f"   Score: {worst['score']:.2f}%")
        
        print("\n" + "="*70)


if __name__ == "__main__":
    # Znajdź najnowszy plik wyników V2
    results_dir = Path(".")
    results_files = sorted(results_dir.glob("gridsearch_results_v2_*.json"), reverse=True)
    
    if results_files:
        latest_file = results_files[0]
        print(f"📁 Używam: {latest_file}")
        
        visualizer = GridSearchVisualizerV2(str(latest_file))
        
        # Stwórz wszystkie wykresy
        visualizer.print_summary()
        print("\n🎨 Generowanie wizualizacji V2...\n")
        
        visualizer.create_interactive_heatmap_plotly("heatmap_gridsearch_v2_interactive.html")
        visualizer.create_3d_surface_plot("heatmap_gridsearch_v2_3d.html")
        visualizer.create_ranking_table("gridsearch_ranking_v2.html", top_n=10)
        
        print("\n" + "="*70)
        print("✅ Wszystkie wykresy V2 zostały wygenerowane!")
        print("="*70)
    else:
        print("❌ Nie znaleziono pliku wyników gridsearch_results_v2_*.json")
        print("   Najpierw uruchom: python3 grid_search_optimization_v2.py")
