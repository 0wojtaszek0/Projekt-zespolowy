"""
IMPROVED VISUALIZATION MODULE v2 - ALL CHARTS CORRECTED
Fixes for age pyramids, population trends, households, and gender distribution
- Proper age group handling (0-4, 5-9, ..., 90+)
- Consistent styling across all charts
- Better color schemes and labels
- Improved interactivity
"""

from typing import Dict, List
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd


class ImprovedSimulationVisualizer:
    """Enhanced visualization with all corrections and improvements."""
    
    def __init__(self, yearly_stats: Dict[int, Dict]) -> None:
        """Initialize visualizer with yearly statistics."""
        self.yearly_stats = yearly_stats
        self.styles = {
            'male_color': '#1f77b4',      # Dark blue
            'female_color': '#d62728',    # Dark red
            'population_color': '#2ca02c',
            'household_color': '#ff7f0e',
            'font_family': 'Arial, sans-serif',
        }
    
    def _get_age_order(self) -> List[str]:
        """Return consistent age group order."""
        age_order = []
        for start in range(0, 90, 5):
            age_order.append(f"{start}-{start+4}")
        age_order.append("90+")  # Consistent final group
        return age_order
    
    # ========================================================================
    # AGE PYRAMID - STATIC (FINAL YEAR)
    # ========================================================================
    
    def plot_interactive_age_pyramid(
        self,
        output_file: str = "piramida_wieku_rok_50.html"
    ) -> None:
        """Create interactive demographic age pyramid (GUS style) for final year."""
        years = sorted(self.yearly_stats.keys())
        
        if not years:
            print("No data to visualize")
            return
        
        final_year = years[-1]
        pyramid = self.yearly_stats[final_year].get("age_pyramid", {})
        
        age_order = self._get_age_order()
        
        # Extract data with safe handling
        males = []
        females = []
        for age_bin in age_order:
            if age_bin in pyramid:
                males.append(-pyramid[age_bin].get("male", 0))
                females.append(pyramid[age_bin].get("female", 0))
            else:
                males.append(0)
                females.append(0)
        
        # Create figure
        fig = go.Figure()
        
        # Add male bars (left side, negative)
        fig.add_trace(go.Bar(
            y=age_order,
            x=males,
            name="Mężczyźni",
            orientation="h",
            marker_color=self.styles['male_color'],
            hovertemplate="<b>%{y}</b><br>Mężczyźni: %{x:.0f}<extra></extra>",
            showlegend=True,
        ))
        
        # Add female bars (right side, positive)
        fig.add_trace(go.Bar(
            y=age_order,
            x=females,
            name="Kobiety",
            orientation="h",
            marker_color=self.styles['female_color'],
            hovertemplate="<b>%{y}</b><br>Kobiety: %{x:.0f}<extra></extra>",
            showlegend=True,
        ))
        
        # Calculate symmetric x-axis limits
        all_vals = [abs(x) for x in males + females if x != 0]
        max_val = max(all_vals) if all_vals else 1000
        x_limit = max_val * 1.15
        
        fig.update_layout(
            title={
                "text": f"<b>Piramida wieku populacji – Rok {final_year}</b><br><sub>Symulacja 50,000 agentów (50 lat)</sub>",
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 18}
            },
            xaxis_title="Liczba osób",
            yaxis_title="Grupy wieku",
            barmode="overlay",
            height=700,
            width=1100,
            hovermode="closest",
            plot_bgcolor="white",
            paper_bgcolor="white",
            xaxis=dict(
                zeroline=True,
                zerolinewidth=2.5,
                zerolinecolor="black",
                range=[-x_limit, x_limit],
                showgrid=True,
                gridwidth=1,
                gridcolor="rgba(200,200,200,0.3)",
                tickformat=".0f",
            ),
            yaxis=dict(
                showgrid=False,
                categoryorder="array",
                categoryarray=age_order,
            ),
            font=dict(family=self.styles['font_family'], size=12),
            legend=dict(
                x=0.5,
                y=-0.10,
                xanchor="center",
                yanchor="top",
                orientation="h",
                bgcolor="rgba(255, 255, 255, 0.9)",
                bordercolor="gray",
                borderwidth=1.5,
            ),
            margin=dict(l=120, r=100, b=140, t=140),
        )
        
        fig.write_html(output_file)
        print(f"✓ Piramida wieku zapisana do {output_file}")
    
    # ========================================================================
    # AGE PYRAMID - ANIMATED WITH SLIDER
    # ========================================================================
    
    def create_animated_age_pyramid(
        self,
        output_file: str = "piramida_wieku_animowana.html"
    ) -> None:
        """Create animated demographic age pyramid with year slider."""
        years = sorted(self.yearly_stats.keys())
        
        if not years:
            print("No data to visualize")
            return
        
        age_order = self._get_age_order()
        
        # Prepare data for all years
        all_data = {}
        for year in years:
            pyramid = self.yearly_stats[year].get("age_pyramid", {})
            males = []
            females = []
            for age_bin in age_order:
                if age_bin in pyramid:
                    males.append(-pyramid[age_bin].get("male", 0))
                    females.append(pyramid[age_bin].get("female", 0))
                else:
                    males.append(0)
                    females.append(0)
            all_data[year] = {"males": males, "females": females}
        
        # Calculate uniform x-axis limits across all years
        max_val = 0
        for year in years:
            males = all_data[year]["males"]
            females = all_data[year]["females"]
            all_vals = [abs(x) for x in males + females if x != 0]
            if all_vals:
                max_val = max(max_val, max(all_vals))
        x_limit = max_val * 1.15
        
        # Create figure with frames for animation
        first_year = years[0]
        data = all_data[first_year]
        
        fig = go.Figure()
        
        # Add initial traces
        fig.add_trace(go.Bar(
            y=age_order,
            x=data["males"],
            name="Mężczyźni",
            orientation="h",
            marker_color=self.styles['male_color'],
            hovertemplate="<b>%{y}</b><br>Mężczyźni: %{x:.0f}<extra></extra>",
            showlegend=True,
        ))
        
        fig.add_trace(go.Bar(
            y=age_order,
            x=data["females"],
            name="Kobiety",
            orientation="h",
            marker_color=self.styles['female_color'],
            hovertemplate="<b>%{y}</b><br>Kobiety: %{x:.0f}<extra></extra>",
            showlegend=True,
        ))
        
        # Create frames for each year
        frames = []
        for year in years:
            data = all_data[year]
            frame = go.Frame(
                data=[
                    go.Bar(y=age_order, x=data["males"], marker_color=self.styles['male_color']),
                    go.Bar(y=age_order, x=data["females"], marker_color=self.styles['female_color'])
                ],
                name=str(year),
                layout=go.Layout(
                    title_text=f"<b>Piramida wieku – Rok {year}</b><br><sub>Symulacja 50,000 agentów</sub>"
                )
            )
            frames.append(frame)
        
        fig.frames = frames
        
        # Update layout with slider
        fig.update_layout(
            title={
                "text": f"<b>Piramida wieku – Rok {first_year}</b><br><sub>Symulacja 50,000 agentów</sub>",
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 18}
            },
            xaxis_title="Liczba osób",
            yaxis_title="Grupy wieku",
            barmode="overlay",
            height=700,
            width=1100,
            hovermode="closest",
            plot_bgcolor="white",
            paper_bgcolor="white",
            xaxis=dict(
                zeroline=True,
                zerolinewidth=2.5,
                zerolinecolor="black",
                range=[-x_limit, x_limit],
                showgrid=True,
                gridwidth=1,
                gridcolor="rgba(200,200,200,0.3)",
                tickformat=".0f",
            ),
            yaxis=dict(
                showgrid=False,
                categoryorder="array",
                categoryarray=age_order,
            ),
            font=dict(family=self.styles['font_family'], size=12),
            legend=dict(
                x=0.5,
                y=-0.10,
                xanchor="center",
                yanchor="top",
                orientation="h",
                bgcolor="rgba(255, 255, 255, 0.9)",
                bordercolor="gray",
                borderwidth=1.5,
            ),
            updatemenus=[
                dict(
                    type="buttons",
                    showactive=False,
                    buttons=[
                        dict(label="▶ Play", method="animate",
                             args=[None, {
                                 "frame": {"duration": 300, "redraw": True},
                                 "fromcurrent": True,
                                 "transition": {"duration": 300}
                             }]),
                        dict(label="⏸ Pause", method="animate",
                             args=[[None], {
                                 "frame": {"duration": 0, "redraw": True},
                                 "mode": "immediate",
                                 "transition": {"duration": 0}
                             }])
                    ],
                    x=0.05,
                    y=1.15,
                )
            ],
            sliders=[{
                "active": 0,
                "yanchor": "top",
                "y": -0.15,
                "xanchor": "left",
                "currentvalue": {
                    "prefix": "Rok: ",
                    "visible": True,
                    "xanchor": "center",
                    "font": {"size": 13}
                },
                "pad": {"b": 10, "t": 50},
                "len": 0.9,
                "x": 0.05,
                "steps": [
                    {
                        "args": [[str(year)], {
                            "frame": {"duration": 300, "redraw": True},
                            "mode": "immediate",
                            "transition": {"duration": 300}
                        }],
                        "method": "animate",
                        "label": str(year)
                    }
                    for year in years
                ]
            }],
            margin=dict(l=120, r=100, b=180, t=150),
        )
        
        fig.write_html(output_file)
        print(f"✓ Animowana piramida wieku zapisana do {output_file}")
    
    # ========================================================================
    # POPULATION TRENDS
    # ========================================================================
    
    def plot_population_trends(
        self,
        output_file: str = "population_trends.html"
    ) -> None:
        """Create population trends visualization."""
        years = sorted(self.yearly_stats.keys())
        
        if not years:
            print("No data to visualize")
            return
        
        populations = []
        multimorbidity = []
        disability_scores = []
        
        for year in years:
            stats = self.yearly_stats[year]
            populations.append(stats.get("total_population", 0))
            multimorbidity.append(stats.get("multimorbidity_cases", 0))
            disability_scores.append(stats.get("average_disability_score", 0))
        
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=("Liczba ludności", "Liczba przypadków multimorbidności", "Średni wskaźnik niepełnosprawności"),
            shared_xaxes=True,
            vertical_spacing=0.12,
            specs=[[{"secondary_y": False}], [{"secondary_y": False}], [{"secondary_y": False}]]
        )
        
        # Population trace
        fig.add_trace(
            go.Scatter(
                x=years,
                y=populations,
                name="Populacja",
                mode="lines+markers",
                line=dict(color=self.styles['population_color'], width=3),
                marker=dict(size=6),
                hovertemplate="Rok %{x}: %{y:,.0f} osób<extra></extra>"
            ),
            row=1, col=1
        )
        
        # Multimorbidity trace
        fig.add_trace(
            go.Scatter(
                x=years,
                y=multimorbidity,
                name="Multimorbidność",
                mode="lines+markers",
                line=dict(color="#ff7f0e", width=3),
                marker=dict(size=6),
                hovertemplate="Rok %{x}: %{y:.0f} przypadków<extra></extra>"
            ),
            row=2, col=1
        )
        
        # Disability trace
        fig.add_trace(
            go.Scatter(
                x=years,
                y=disability_scores,
                name="Niepełnosprawność",
                mode="lines+markers",
                line=dict(color="#d62728", width=3),
                marker=dict(size=6),
                hovertemplate="Rok %{x}: %{y:.4f}<extra></extra>"
            ),
            row=3, col=1
        )
        
        # Update axes
        fig.update_xaxes(title_text="Rok symulacji", row=3, col=1)
        fig.update_yaxes(title_text="Liczba osób", row=1, col=1)
        fig.update_yaxes(title_text="Liczba przypadków", row=2, col=1)
        fig.update_yaxes(title_text="Wskaźnik (0-1)", row=3, col=1)
        
        fig.update_layout(
            title="<b>Trendy populacji – 50 lat symulacji</b>",
            height=900,
            width=1100,
            hovermode="x unified",
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(family=self.styles['font_family'], size=12),
            margin=dict(l=100, r=100, b=100, t=120),
        )
        
        for i in range(1, 4):
            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="rgba(200,200,200,0.3)", row=i, col=1)
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="rgba(200,200,200,0.3)", row=i, col=1)
        
        fig.write_html(output_file)
        print(f"✓ Trendy populacji zapisane do {output_file}")
    
    # ========================================================================
    # HOUSEHOLD TRENDS
    # ========================================================================
    
    def plot_households_trends(
        self,
        output_file: str = "households_trends.html"
    ) -> None:
        """Create household trends visualization."""
        years = sorted(self.yearly_stats.keys())
        
        if not years:
            print("No data to visualize")
            return
        
        households = []
        avg_size = []
        
        for year in years:
            stats = self.yearly_stats[year]
            households.append(stats.get("number_of_households", 0))
            avg_size.append(stats.get("average_household_size", 0))
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=("Liczba gospodarstw domowych", "Średni rozmiar gospodarstwa"),
            shared_xaxes=True,
            vertical_spacing=0.15,
        )
        
        # Households trace
        fig.add_trace(
            go.Scatter(
                x=years,
                y=households,
                name="Gospodarstwa",
                mode="lines+markers",
                line=dict(color=self.styles['household_color'], width=3),
                marker=dict(size=6),
                hovertemplate="Rok %{x}: %{y:,.0f}<extra></extra>"
            ),
            row=1, col=1
        )
        
        # Average size trace
        fig.add_trace(
            go.Scatter(
                x=years,
                y=avg_size,
                name="Średni rozmiar",
                mode="lines+markers",
                line=dict(color="#2ca02c", width=3),
                marker=dict(size=6),
                hovertemplate="Rok %{x}: %{y:.2f} osób<extra></extra>"
            ),
            row=2, col=1
        )
        
        fig.update_xaxes(title_text="Rok symulacji", row=2, col=1)
        fig.update_yaxes(title_text="Liczba", row=1, col=1)
        fig.update_yaxes(title_text="Rozmiar (osób)", row=2, col=1)
        
        fig.update_layout(
            title="<b>Trendy gospodarstw domowych – 50 lat symulacji</b>",
            height=700,
            width=1100,
            hovermode="x unified",
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(family=self.styles['font_family'], size=12),
            margin=dict(l=100, r=100, b=100, t=120),
        )
        
        for i in range(1, 3):
            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="rgba(200,200,200,0.3)", row=i, col=1)
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="rgba(200,200,200,0.3)", row=i, col=1)
        
        fig.write_html(output_file)
        print(f"✓ Trendy gospodarstw zapisane do {output_file}")
    
    # ========================================================================
    # GENDER DISTRIBUTION
    # ========================================================================
    
    def plot_gender_distribution(
        self,
        output_file: str = "gender_distribution.html"
    ) -> None:
        """Create gender distribution over time."""
        years = sorted(self.yearly_stats.keys())
        
        if not years:
            print("No data to visualize")
            return
        
        males_pct = []
        females_pct = []
        
        for year in years:
            stats = self.yearly_stats[year]
            male = stats.get("male_count", 0)
            female = stats.get("female_count", 0)
            total = male + female
            
            if total > 0:
                males_pct.append(100 * male / total)
                females_pct.append(100 * female / total)
            else:
                males_pct.append(50)
                females_pct.append(50)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=years,
            y=males_pct,
            name="Mężczyźni",
            mode="lines+markers",
            line=dict(color=self.styles['male_color'], width=3),
            marker=dict(size=6),
            hovertemplate="Rok %{x}: %{y:.1f}%<extra></extra>",
            fill="tonexty" if len(females_pct) > 0 else None,
        ))
        
        fig.add_trace(go.Scatter(
            x=years,
            y=females_pct,
            name="Kobiety",
            mode="lines+markers",
            line=dict(color=self.styles['female_color'], width=3),
            marker=dict(size=6),
            hovertemplate="Rok %{x}: %{y:.1f}%<extra></extra>",
            fill="tozeroy",
        ))
        
        fig.update_layout(
            title="<b>Rozkład płci w populacji – 50 lat symulacji</b>",
            xaxis_title="Rok symulacji",
            yaxis_title="Procent populacji (%)",
            height=600,
            width=1100,
            hovermode="x unified",
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(family=self.styles['font_family'], size=12),
            xaxis=dict(showgrid=True, gridwidth=1, gridcolor="rgba(200,200,200,0.3)"),
            yaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor="rgba(200,200,200,0.3)",
                range=[0, 100]
            ),
            margin=dict(l=100, r=100, b=100, t=120),
        )
        
        fig.write_html(output_file)
        print(f"✓ Rozkład płci zapisany do {output_file}")
    
    # ========================================================================
    # GENERATE ALL PLOTS
    # ========================================================================
    
    def generate_all_plots(self, output_dir: str = ".") -> None:
        """Generate all visualization files."""
        import os
        
        print("\n" + "="*80)
        print("GENERATING VISUALIZATIONS - IMPROVED VERSION")
        print("="*80 + "\n")
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Generate all plots
        self.plot_interactive_age_pyramid(os.path.join(output_dir, "piramida_wieku_rok_50.html"))
        self.create_animated_age_pyramid(os.path.join(output_dir, "piramida_wieku_animowana.html"))
        self.plot_population_trends(os.path.join(output_dir, "population_trends.html"))
        self.plot_households_trends(os.path.join(output_dir, "households_trends.html"))
        self.plot_gender_distribution(os.path.join(output_dir, "gender_distribution.html"))
        
        print("\n" + "="*80)
        print("✓ ALL VISUALIZATIONS GENERATED SUCCESSFULLY")
        print("="*80 + "\n")
