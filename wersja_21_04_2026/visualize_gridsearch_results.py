"""
Wizualizacja wyników Grid Search - heatmap'y i interaktywne wykresy Plotly
"""

import json
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path


class GridSearchVisualizer:
    def __init__(self, results_file: str):
        """
        Załaduj wyniki z JSON'a
        
        Args:
            results_file: Ścieżka do pliku JSON z wynikami gridsearch'a
        """
        with open(results_file, 'r') as f:
            self.raw_results = json.load(f)
        
        self.results_df = pd.DataFrame([
            {
                'fertility_multiplier': r['params']['fertility_multiplier'],
                'mortality_multiplier': r['params']['mortality_multiplier'],
                'score': r['score']
            }
            for r in self.raw_results
        ])
        
        print(f"✓ Załadowano {len(self.results_df)} kombinacji parametrów")
        print(f"✓ Najlepszy score: {self.results_df['score'].max():.4f}")
        print(f"✓ Najgorszy score: {self.results_df['score'].min():.4f}")
    
    def create_interactive_heatmap_plotly(self, output_file: str = "heatmap_gridsearch_interactive.html"):
        """
        Stwórz interaktywny heatmap w Plotly
        """
        # Pivot table dla heatmap'a
        heatmap_data = self.results_df.pivot_table(
            index='mortality_multiplier',
            columns='fertility_multiplier',
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
            x=[best_row['fertility_multiplier']],
            y=[best_row['mortality_multiplier']],
            mode='markers',
            marker=dict(size=15, color='red', symbol='star', line=dict(color='darkred', width=2)),
            name=f"Best: {best_row['score']:.2f}%",
            hovertemplate=f"<b>Fertility:</b> %{{x:.3f}}<br><b>Mortality:</b> %{{y:.3f}}<br><b>Score:</b> {best_row['score']:.2f}%<extra></extra>"
        ))
        
        fig.update_layout(
            title={
                'text': "<b>Grid Search Results: Population Change (%)</b><br><sub>2 Parameters: Fertility Multiplier vs Mortality Multiplier</sub>",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18}
            },
            xaxis_title="<b>Fertility Multiplier</b>",
            yaxis_title="<b>Mortality Multiplier</b>",
            hovermode='closest',
            width=900,
            height=700,
            font=dict(size=12),
            paper_bgcolor='white',
            plot_bgcolor='white'
        )
        
        fig.write_html(output_file)
        print(f"✓ Zapisano mapę ciepła (Plotly): {output_file}")
    
    def create_heatmap_matplotlib(self, output_file: str = "heatmap_gridsearch_matplotlib.png"):
        """
        Stwórz statyczną heatmap'ę w Matplotlib (wyższa jakość)
        """
        # Pivot table
        heatmap_data = self.results_df.pivot_table(
            index='mortality_multiplier',
            columns='fertility_multiplier',
            values='score'
        )
        
        # Sortuj
        heatmap_data = heatmap_data.sort_index(ascending=False)
        heatmap_data = heatmap_data[[float(x) for x in sorted(heatmap_data.columns)]]
        
        # Stwórz figurę
        fig, ax = plt.subplots(figsize=(12, 9), dpi=150)
        
        # Heatmap
        sns.heatmap(
            heatmap_data,
            annot=True,
            fmt='.2f',
            cmap='RdYlGn',
            cbar_kws={'label': 'Score: Population Change (%)'},
            ax=ax,
            linewidths=0.5,
            linecolor='gray',
            vmin=heatmap_data.values.min(),
            vmax=heatmap_data.values.max()
        )
        
        # Znajdź i zaznacz najlepszy punkt
        best_row = self.results_df.loc[self.results_df['score'].idxmax()]
        best_fert = best_row['fertility_multiplier']
        best_mort = best_row['mortality_multiplier']
        
        # Znajdź indeksy w DataFrame'ie
        col_idx = list(heatmap_data.columns).index(best_fert)
        row_idx = list(heatmap_data.index).index(best_mort)
        
        # Dodaj gwiazdkę dla najlepszego wyniku
        ax.add_patch(plt.Rectangle((col_idx, row_idx), 1, 1, fill=False, 
                                   edgecolor='red', lw=3))
        ax.text(col_idx + 0.5, row_idx + 0.3, '★', fontsize=20, color='red', 
               ha='center', va='center', weight='bold')
        
        ax.set_xlabel('Fertility Multiplier', fontsize=14, weight='bold')
        ax.set_ylabel('Mortality Multiplier', fontsize=14, weight='bold')
        ax.set_title('Grid Search Results: Population Change Heatmap\n(★ = Best Parameters)', 
                    fontsize=16, weight='bold', pad=20)
        
        # Rotuj tick labels
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
        ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        print(f"✓ Zapisano mapę ciepła (Matplotlib): {output_file}")
        plt.close()
    
    def create_3d_surface_plot(self, output_file: str = "heatmap_gridsearch_3d.html"):
        """
        Stwórz 3D surface plot z Plotly
        """
        # Pivot table
        heatmap_data = self.results_df.pivot_table(
            index='mortality_multiplier',
            columns='fertility_multiplier',
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
                'text': "<b>3D Surface: Population Change (Score)</b><br><sub>Fertility Multiplier × Mortality Multiplier</sub>",
                'x': 0.5,
                'xanchor': 'center'
            },
            scene=dict(
                xaxis_title='Fertility Multiplier',
                yaxis_title='Mortality Multiplier',
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
    
    def create_ranking_table(self, output_file: str = "gridsearch_ranking.html", top_n: int = 10):
        """
        Stwórz interaktywną tabelę z top N wynikami
        """
        ranking = self.results_df.nlargest(top_n, 'score').reset_index(drop=True)
        ranking['Rank'] = range(1, len(ranking) + 1)
        ranking = ranking[['Rank', 'fertility_multiplier', 'mortality_multiplier', 'score']]
        ranking.columns = ['Rank', 'Fertility', 'Mortality', 'Score (%)']
        
        # Format wartości
        ranking['Fertility'] = ranking['Fertility'].apply(lambda x: f"{x:.3f}")
        ranking['Mortality'] = ranking['Mortality'].apply(lambda x: f"{x:.3f}")
        ranking['Score (%)'] = ranking['Score (%)'].apply(lambda x: f"{x:.2f}")
        
        # Stwórz tabelę Plotly
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=list(ranking.columns),
                fill_color='#1f77b4',
                align='center',
                font=dict(color='white', size=12, family='Arial')
            ),
            cells=dict(
                values=[ranking[col] for col in ranking.columns],
                fill_color=[
                    ['#e8f4f8' if i % 2 == 0 else 'white' for i in range(len(ranking))]
                    for _ in ranking.columns
                ],
                align='center',
                font=dict(size=11, family='Arial'),
                height=30
            )
        )])
        
        fig.update_layout(
            title={
                'text': f"<b>Top {top_n} Grid Search Results</b>",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18}
            },
            height=450 + top_n * 30,
            width=600,
            margin=dict(l=50, r=50, t=100, b=50),
            paper_bgcolor='white',
            plot_bgcolor='white'
        )
        
        fig.write_html(output_file)
        print(f"✓ Zapisano ranking (Top {top_n}): {output_file}")
    
    def print_summary(self):
        """
        Wypisz podsumowanie wyników
        """
        print("\n" + "="*70)
        print("PODSUMOWANIE WYNIKÓW GRID SEARCH")
        print("="*70)
        
        best = self.results_df.loc[self.results_df['score'].idxmax()]
        worst = self.results_df.loc[self.results_df['score'].idxmin()]
        
        print(f"\n🏆 NAJLEPSZE PARAMETRY:")
        print(f"   Fertility Multiplier: {best['fertility_multiplier']:.3f}")
        print(f"   Mortality Multiplier: {best['mortality_multiplier']:.3f}")
        print(f"   Score (zmiana populacji): {best['score']:.2f}%")
        
        print(f"\n📊 STATYSTYKI:")
        print(f"   Średnia score: {self.results_df['score'].mean():.2f}%")
        print(f"   Mediana score: {self.results_df['score'].median():.2f}%")
        print(f"   Std dev: {self.results_df['score'].std():.2f}%")
        print(f"   Min score: {worst['score']:.2f}%")
        print(f"   Max score: {best['score']:.2f}%")
        
        print(f"\n⚠️ NAJGORSZE PARAMETRY:")
        print(f"   Fertility Multiplier: {worst['fertility_multiplier']:.3f}")
        print(f"   Mortality Multiplier: {worst['mortality_multiplier']:.3f}")
        print(f"   Score: {worst['score']:.2f}%")
        
        print("\n" + "="*70)


if __name__ == "__main__":
    # Znajdź najnowszy plik wyników
    results_dir = Path(".")
    results_files = sorted(results_dir.glob("gridsearch_results_*.json"), reverse=True)
    
    if results_files:
        latest_file = results_files[0]
        print(f"📁 Używam: {latest_file}")
        
        visualizer = GridSearchVisualizer(str(latest_file))
        
        # Stwórz wszystkie wykresy
        visualizer.print_summary()
        print("\n🎨 Generowanie wizualizacji...\n")
        
        visualizer.create_interactive_heatmap_plotly("heatmap_gridsearch_interactive.html")
        visualizer.create_heatmap_matplotlib("heatmap_gridsearch_matplotlib.png")
        visualizer.create_3d_surface_plot("heatmap_gridsearch_3d.html")
        visualizer.create_ranking_table("gridsearch_ranking.html", top_n=10)
        
        print("\n" + "="*70)
        print("✅ Wszystkie wykresy zostały wygenerowane!")
        print("="*70)
    else:
        print("❌ Nie znaleziono pliku wyników gridsearch_results_*.json")
        print("   Najpierw uruchom: python3 grid_search_optimization.py")
