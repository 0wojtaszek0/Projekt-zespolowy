"""
Enhanced GridSearch Optimization with Heatmap Visualization

Creates heatmaps showing how different parameter combinations affect the score.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.subplots as sp
from sklearn.model_selection import ParameterGrid
from itertools import combinations


class GridSearchWithHeatmap:
    def __init__(self, param_grid, scoring_function, n_iter=10):
        """
        param_grid: Dictionary of parameters to optimize.
        scoring_function: Function to evaluate the simulation.
        n_iter: Number of iterations to repeat the GridSearch for stability.
        """
        self.param_grid = param_grid
        self.scoring_function = scoring_function
        self.n_iter = n_iter
        self.results = []  # Store all results for heatmap
        self.best_params = None
        self.best_score = -float('inf')

    def optimize(self):
        """
        Perform GridSearch and collect all results for heatmap visualization.
        """
        print("Running GridSearch and collecting results for heatmap...")
        
        for i in range(self.n_iter):
            print(f"Iteration {i + 1}/{self.n_iter}")
            for params in ParameterGrid(self.param_grid):
                # Skip invalid parameter combinations
                if params['birth_rate'] < params['mortality_rate']:
                    continue

                score = self.scoring_function(**params)
                
                # Store result with parameters and score
                result = params.copy()
                result['score'] = score
                self.results.append(result)
                
                # Track best parameters
                if score > self.best_score:
                    self.best_score = score
                    self.best_params = params.copy()

        print("Final best parameters:", self.best_params)
        print("Final best score:", self.best_score)
        return self.best_params, self.best_score

    def create_heatmaps(self, output_file='heatmap_gridsearch.html'):
        """
        Create interactive heatmaps for major parameter pairs.
        
        Args:
            output_file: Name of the output HTML file
        """
        if not self.results:
            print("No results to visualize. Run optimize() first.")
            return
        
        # Convert results to DataFrame
        df = pd.DataFrame(self.results)
        
        # Get unique parameters (excluding score)
        params = [col for col in df.columns if col != 'score']
        
        # Select main parameter pairs for visualization
        main_pairs = [
            ('birth_rate', 'mortality_rate'),
            ('fertility_multiplier', 'mortality_multiplier'),
            ('birth_rate', 'fertility_multiplier'),
        ]
        
        # Create subplots
        fig = sp.make_subplots(
            rows=1, cols=3,
            subplot_titles=[f'{p[0]} vs {p[1]}' for p in main_pairs],
            specs=[[{'type': 'heatmap'}, {'type': 'heatmap'}, {'type': 'heatmap'}]]
        )
        
        # Fix other parameters to their best values
        best_params = self.best_params.copy()
        
        for col_idx, (param1, param2) in enumerate(main_pairs, 1):
            # Create pivot table for heatmap - use all data without filtering other params
            pivot_data = df.copy()
            
            # Get unique values for the two main parameters
            x_values = sorted(pivot_data[param2].unique())
            y_values = sorted(pivot_data[param1].unique())
            
            # Create matrix
            matrix = np.full((len(y_values), len(x_values)), np.nan)
            
            for i, y_val in enumerate(y_values):
                for j, x_val in enumerate(x_values):
                    mask = (pivot_data[param1] == y_val) & (pivot_data[param2] == x_val)
                    if mask.any():
                        # Average score if multiple values
                        matrix[i, j] = pivot_data[mask]['score'].mean()
            
            # Add heatmap to subplot
            heatmap = go.Heatmap(
                z=matrix,
                x=np.round(x_values, 6),
                y=np.round(y_values, 6),
                colorscale='RdYlGn',
                colorbar=dict(
                    title=f"Score",
                    len=0.7
                ),
                hovertemplate=f'<b>{param2}:</b> %{{x:.6f}}<br><b>{param1}:</b> %{{y:.6f}}<br><b>Score:</b> %{{z:.0f}}<extra></extra>',
                name=''
            )
            
            fig.add_trace(heatmap, row=1, col=col_idx)
            
            # Update axes labels
            fig.update_xaxes(title_text=param2, row=1, col=col_idx, tickangle=-45)
            fig.update_yaxes(title_text=param1, row=1, col=col_idx)
        
        # Update layout
        fig.update_layout(
            title={
                'text': 'GridSearch Parameter Optimization - Heatmaps<br><sub>Score values for parameter combinations (aggregated across all other parameters)</sub>',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18}
            },
            height=700,
            width=2000,
            showlegend=False,
            font=dict(size=10),
            margin=dict(b=150)
        )
        
        fig.write_html(output_file)
        print(f"\n✅ Heatmap saved to {output_file}")

    def create_3d_surface_plots(self, output_file='heatmap_3d_gridsearch.html'):
        """
        Create 3D surface plots for parameter optimization visualization.
        
        Args:
            output_file: Name of the output HTML file
        """
        if not self.results:
            print("No results to visualize. Run optimize() first.")
            return
        
        df = pd.DataFrame(self.results)
        
        # Select main parameter pairs for 3D visualization
        main_pairs = [
            ('fertility_multiplier', 'mortality_multiplier'),
            ('birth_rate', 'fertility_multiplier'),
            ('birth_rate', 'mortality_rate'),
        ]
        
        # Create individual 3D surface plots
        for param1, param2 in main_pairs:
            # Use all data
            pivot_data = df.copy()
            
            # Get unique values
            x_values = sorted(pivot_data[param2].unique())
            y_values = sorted(pivot_data[param1].unique())
            
            # Create matrix
            matrix = np.full((len(y_values), len(x_values)), np.nan)
            
            for i, y_val in enumerate(y_values):
                for j, x_val in enumerate(x_values):
                    mask = (pivot_data[param1] == y_val) & (pivot_data[param2] == x_val)
                    if mask.any():
                        matrix[i, j] = pivot_data[mask]['score'].mean()
            
            # Fill NaN with interpolation or nearest valid value
            z_clean = matrix.copy()
            # Replace NaN with minimum value for better surface rendering
            valid_values = z_clean[~np.isnan(z_clean)]
            if len(valid_values) > 0:
                z_clean = np.where(np.isnan(z_clean), valid_values.min(), z_clean)
            
            # Create 3D surface plot
            fig = go.Figure(data=[go.Surface(
                x=x_values,
                y=y_values,
                z=z_clean,
                colorscale='Viridis',
                colorbar=dict(
                    title='Score',
                    thickness=15,
                    len=0.75
                ),
                hovertemplate=f'<b>{param2}:</b> %{{x:.6f}}<br><b>{param1}:</b> %{{y:.6f}}<br><b>Score:</b> %{{z:.0f}}<extra></extra>',
                opacity=0.95
            )])
            
            fig.update_layout(
                title={
                    'text': f'3D Surface: {param1} vs {param2}<br><sub>Score optimization landscape</sub>',
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 13}
                },
                scene=dict(
                    xaxis_title=param2,
                    yaxis_title=param1,
                    zaxis_title='Score',
                    xaxis=dict(showgrid=True, gridwidth=1, gridcolor='lightgray'),
                    yaxis=dict(showgrid=True, gridwidth=1, gridcolor='lightgray'),
                    zaxis=dict(showgrid=True, gridwidth=1, gridcolor='lightgray'),
                    camera=dict(
                        eye=dict(x=1.5, y=1.5, z=1.2)
                    )
                ),
                height=750,
                width=1050,
                font=dict(size=10),
                margin=dict(l=0, r=0, t=100, b=0),
                hovermode='closest',
                showlegend=False
            )
            
            # Save individual file
            filename = f'heatmap_3d_{param1}_vs_{param2}.html'
            fig.write_html(filename)
            print(f"✅ 3D surface plot saved to {filename}")


def create_parameter_grid():
    """Create 4D parameter grid for optimization (no migration)."""
    return {
        "birth_rate": [0.01 + i * 0.002 for i in range(25)],
        "mortality_rate": [0.0005 + i * 0.0001 for i in range(25)],
        "fertility_multiplier": [0.5 + i * 0.2 for i in range(10)],
        "mortality_multiplier": [0.5 + i * 0.2 for i in range(10)]
    }


def simulation_scoring_function(birth_rate, mortality_rate, fertility_multiplier, mortality_multiplier):
    """Scoring function for 4D simulation parameters (no migration)."""
    initial_population = 50000
    final_population = initial_population

    for year in range(50):
        births = final_population * birth_rate * fertility_multiplier
        deaths = final_population * mortality_rate * mortality_multiplier
        final_population += births - deaths

        if final_population < 0:
            final_population = 0
            break

    target_population = 30000
    score = final_population - target_population
    return score


if __name__ == "__main__":
    print("=" * 80)
    print("GRIDSEARCH OPTIMIZATION WITH HEATMAP VISUALIZATION")
    print("=" * 80)
    print()
    
    param_grid = create_parameter_grid()
    
    optimizer = GridSearchWithHeatmap(
        param_grid=param_grid,
        scoring_function=simulation_scoring_function,
        n_iter=10
    )
    
    # Run optimization
    best_params, best_score = optimizer.optimize()
    print()
    
    # Create visualizations
    print("\nGenerating visualizations...")
    optimizer.create_heatmaps('heatmap_gridsearch.html')
    optimizer.create_3d_surface_plots()
    
    print("\n" + "=" * 80)
    print("VISUALIZATION COMPLETE")
    print("=" * 80)
