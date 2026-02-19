"""
Module for interactive visualization of simulation results using Plotly.
Includes age pyramids, population trends, and household statistics.
"""

from typing import Dict, List
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd


class SimulationVisualizer:
    """
    Handles visualization of simulation results.
    
    Attributes:
        yearly_stats: Dictionary of yearly statistics from simulation
    """
    
    def __init__(self, yearly_stats: Dict[int, Dict]) -> None:
        """
        Initialize the visualizer.
        
        Args:
            yearly_stats: Dictionary mapping year numbers to statistics dictionaries
        """
        self.yearly_stats = yearly_stats
    
    def plot_interactive_age_pyramid(
        self,
        output_file: str = "age_pyramid_interactive.html"
    ) -> None:
        """
        Create an interactive age pyramid with year slider.
        
        Args:
            output_file: Path to save the HTML file
        """
        years = sorted(self.yearly_stats.keys())
        
        if not years:
            print("No data to visualize")
            return
        
        # Prepare data for all years
        all_data = {}
        for year in years:
            pyramid = self.yearly_stats[year]["age_pyramid"]
            age_bins = sorted(pyramid.keys(), key=lambda x: int(x.split('-')[0]))
            males = [-pyramid[age]["male"] for age in age_bins]  # Negative for left side
            females = [pyramid[age]["female"] for age in age_bins]
            
            all_data[year] = {
                "age_bins": age_bins,
                "males": males,
                "females": females,
            }
        
        # Create figure with first year
        first_year = years[0]
        data = all_data[first_year]
        
        fig = go.Figure()
        
        # Add male bars (horizontal, negative values)
        fig.add_trace(go.Bar(
            y=data["age_bins"],
            x=data["males"],
            name="Male",
            orientation="h",
            marker_color="lightblue",
            hovertemplate="<b>Age: %{y}</b><br>Male: %{value}<extra></extra>",
        ))
        
        # Add female bars
        fig.add_trace(go.Bar(
            y=data["age_bins"],
            x=data["females"],
            name="Female",
            orientation="h",
            marker_color="lightpink",
            hovertemplate="<b>Age: %{y}</b><br>Female: %{value}<extra></extra>",
        ))
        
        # Create frames for animation
        frames = []
        for year in years:
            data = all_data[year]
            frames.append(go.Frame(
                data=[
                    go.Bar(y=data["age_bins"], x=data["males"], marker_color="lightblue"),
                    go.Bar(y=data["age_bins"], x=data["females"], marker_color="lightpink"),
                ],
                name=str(year)
            ))
        
        fig.frames = frames
        
        # Create slider
        sliders = [
            {
                "active": 0,
                "yanchor": "top",
                "y": 0,
                "xanchor": "left",
                "x": 0.0,
                "len": 0.9,
                "transition": {"duration": 300},
                "pad": {"b": 10, "t": 50},
                "currentvalue": {
                    "prefix": "Year: ",
                    "visible": True,
                    "xanchor": "center",
                },
                "steps": [
                    {
                        "args": [
                            [str(year)],
                            {
                                "frame": {"duration": 300, "redraw": True},
                                "mode": "immediate",
                                "transition": {"duration": 300},
                            }
                        ],
                        "method": "animate",
                        "label": str(year),
                    }
                    for year in years
                ],
            }
        ]
        
        fig.update_layout(
            sliders=sliders,
            barmode="relative",
            title={
                "text": f"<b>Age Pyramid: {first_year}-{years[-1]} Year Projection</b>",
                "x": 0.5,
                "xanchor": "center",
            },
            xaxis_title="Population",
            yaxis_title="Age Group",
            height=700,
            hovermode="closest",
            plot_bgcolor="rgba(240,240,240,0.5)",
        )
        
        fig.write_html(output_file)
        print(f"Age pyramid saved to {output_file}")
    
    def plot_population_trends(
        self,
        output_file: str = "population_trends.html"
    ) -> None:
        """
        Create line plot showing population trends over time.
        
        Args:
            output_file: Path to save the HTML file
        """
        years = sorted(self.yearly_stats.keys())
        populations = [self.yearly_stats[y]["total_population"] for y in years]
        multimorbidity = [self.yearly_stats[y].get("multimorbidity_count", 0) for y in years]
        avg_disability = [self.yearly_stats[y].get("average_disability_score", 0) for y in years]
        
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=("Total Population", "Multimorbidity Cases", "Average Disability Score"),
            specs=[[{"secondary_y": False}], [{"secondary_y": False}], [{"secondary_y": False}]],
        )
        
        # Population
        fig.add_trace(
            go.Scatter(
                x=years, y=populations,
                mode="lines+markers",
                name="Population",
                line=dict(color="blue", width=2),
                hovertemplate="Year %{x}: %{y} people<extra></extra>",
            ),
            row=1, col=1,
        )
        
        # Multimorbidity
        fig.add_trace(
            go.Scatter(
                x=years, y=multimorbidity,
                mode="lines+markers",
                name="Multimorbidity",
                line=dict(color="red", width=2),
                hovertemplate="Year %{x}: %{y} cases<extra></extra>",
            ),
            row=2, col=1,
        )
        
        # Avg Disability
        fig.add_trace(
            go.Scatter(
                x=years, y=avg_disability,
                mode="lines+markers",
                name="Avg Disability",
                line=dict(color="orange", width=2),
                hovertemplate="Year %{x}: %{y:.3f}<extra></extra>",
            ),
            row=3, col=1,
        )
        
        fig.update_xaxes(title_text="Year", row=3, col=1)
        fig.update_yaxes(title_text="Count", row=1, col=1)
        fig.update_yaxes(title_text="Count", row=2, col=1)
        fig.update_yaxes(title_text="Score", row=3, col=1)
        
        fig.update_layout(
            height=800,
            title_text="<b>Population Trends Over 50 Years</b>",
            showlegend=False,
            hovermode="x unified",
            plot_bgcolor="rgba(240,240,240,0.5)",
        )
        
        fig.write_html(output_file)
        print(f"Population trends saved to {output_file}")
    
    def plot_households_trends(
        self,
        output_file: str = "households_trends.html"
    ) -> None:
        """
        Create line plot showing household trends over time.
        
        Args:
            output_file: Path to save the HTML file
        """
        years = sorted(self.yearly_stats.keys())
        households = [self.yearly_stats[y]["num_households"] for y in years]
        avg_size = [self.yearly_stats[y]["average_household_size"] for y in years]
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=("Number of Households", "Average Household Size"),
            vertical_spacing=0.12,
        )
        
        # Households
        fig.add_trace(
            go.Scatter(
                x=years, y=households,
                mode="lines+markers",
                name="Households",
                line=dict(color="green", width=2),
                fill="tozeroy",
                hovertemplate="Year %{x}: %{y} households<extra></extra>",
            ),
            row=1, col=1,
        )
        
        # Avg household size
        fig.add_trace(
            go.Scatter(
                x=years, y=avg_size,
                mode="lines+markers",
                name="Avg Size",
                line=dict(color="purple", width=2),
                hovertemplate="Year %{x}: %{y:.2f} members<extra></extra>",
            ),
            row=2, col=1,
        )
        
        fig.update_xaxes(title_text="Year", row=2, col=1)
        fig.update_yaxes(title_text="Count", row=1, col=1)
        fig.update_yaxes(title_text="Size", row=2, col=1)
        
        fig.update_layout(
            height=700,
            title_text="<b>Household Dynamics Over 50 Years</b>",
            showlegend=False,
            hovermode="x unified",
            plot_bgcolor="rgba(240,240,240,0.5)",
        )
        
        fig.write_html(output_file)
        print(f"Household trends saved to {output_file}")
    
    def plot_gender_distribution(
        self,
        output_file: str = "gender_distribution.html"
    ) -> None:
        """
        Create plot showing male/female distribution over time.
        
        Args:
            output_file: Path to save the HTML file
        """
        years = sorted(self.yearly_stats.keys())
        males = [self.yearly_stats[y]["num_males"] for y in years]
        females = [self.yearly_stats[y]["num_females"] for y in years]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=years, y=males,
            mode="lines+markers",
            name="Male",
            line=dict(color="lightblue", width=2),
            fill="tozeroy",
            hovertemplate="Year %{x}: %{y} males<extra></extra>",
        ))
        
        fig.add_trace(go.Scatter(
            x=years, y=females,
            mode="lines+markers",
            name="Female",
            line=dict(color="lightpink", width=2),
            fill="tozeroy",
            hovertemplate="Year %{x}: %{y} females<extra></extra>",
        ))
        
        fig.update_layout(
            title="<b>Gender Distribution Over Time</b>",
            xaxis_title="Year",
            yaxis_title="Population",
            hovermode="x unified",
            height=600,
            plot_bgcolor="rgba(240,240,240,0.5)",
        )
        
        fig.write_html(output_file)
        print(f"Gender distribution saved to {output_file}")
    
    def generate_all_plots(self, output_dir: str = ".") -> None:
        """
        Generate all visualization plots.
        
        Args:
            output_dir: Directory to save HTML files (default: current directory)
        """
        print("\nGenerating interactive visualizations...")
        self.plot_interactive_age_pyramid(f"{output_dir}/age_pyramid_interactive.html")
        self.plot_population_trends(f"{output_dir}/population_trends.html")
        self.plot_households_trends(f"{output_dir}/households_trends.html")
        self.plot_gender_distribution(f"{output_dir}/gender_distribution.html")
        print("All visualizations generated successfully!")
