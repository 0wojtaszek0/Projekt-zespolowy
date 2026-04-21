"""
Enhanced GridSearch Optimization with 4D Heatmap Visualization

Creates multi-panel heatmaps showing 4D dependency: Z(fertility, mortality, birth_rate, death_rate)
Each heatmap shows fertility_multiplier vs mortality_multiplier for fixed birth_rate and death_rate values.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable, RdYlGn_r
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.model_selection import ParameterGrid
from simulation_engine import SimulationEngine
from disease_model import DiseaseModel


class GridSearchWithHeatmap:
    def __init__(self, param_grid, scoring_function, n_iter=10):
        """
        param_grid: Dictionary of parameters to optimize.
        scoring_function: Function to evaluate the simulation.
        n_iter: Number of iterations to repeat the GridSearch for stability (default=10 dla bardziej wiarygodnych wyników).
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

    def create_4d_heatmaps(self, output_file='heatmap_gridsearch_4d.png'):
        """
        Create multi-panel heatmap showing 4D dependencies using matplotlib.
        X, Y axes: fertility_multiplier vs mortality_multiplier
        Rows: different birth_rate_factor values
        Columns: different death_rate_factor values
        
        Args:
            output_file: Name of the output file (PNG or PDF)
        """
        if not self.results:
            print("No results to visualize. Run optimize() first.")
            return
        
        # Convert results to DataFrame
        df = pd.DataFrame(self.results)
        
        # Main heatmap parameters
        x_param = 'mortality_multiplier'  # Columns in each heatmap
        y_param = 'fertility_multiplier'  # Rows in each heatmap
        
        # Panel parameters - create grid of heatmaps
        row_param = 'birth_rate_factor'
        col_param = 'death_rate_factor'
        
        # Get unique values
        x_values = sorted(df[x_param].unique())
        y_values = sorted(df[y_param].unique())
        row_values = sorted(df[row_param].unique())
        col_values = sorted(df[col_param].unique())
        
        n_rows = len(row_values)
        n_cols = len(col_values)
        
        print(f"Creating {n_rows}x{n_cols} grid of heatmaps using matplotlib...")
        print(f"  X-axis ({x_param}): {x_values}")
        print(f"  Y-axis ({y_param}): {y_values}")
        print(f"  Rows ({row_param}): {row_values}")
        print(f"  Columns ({col_param}): {col_values}")
        
        # Create figure with subplots
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(4*n_cols, 4*n_rows))
        if n_rows == 1:
            axes = axes.reshape(1, -1)
        elif n_cols == 1:
            axes = axes.reshape(-1, 1)
        
        # Get global min/max for consistent color scale
        all_scores = df['score'].values
        z_min = np.nanmin(all_scores)
        z_max = np.nanmax(all_scores)
        
        # Normalize for colormap
        norm = Normalize(vmin=z_min, vmax=z_max)
        cmap = RdYlGn_r
        
        # Create heatmaps for each row, col combination
        for row_idx, row_val in enumerate(row_values):
            for col_idx, col_val in enumerate(col_values):
                ax = axes[row_idx, col_idx]
                
                # Filter data for this panel
                mask = (df[row_param] == row_val) & (df[col_param] == col_val)
                panel_df = df[mask]
                
                if panel_df.empty:
                    ax.text(0.5, 0.5, 'No data', ha='center', va='center')
                    ax.set_xticks([])
                    ax.set_yticks([])
                    continue
                
                # Create matrix for this heatmap
                matrix = np.full((len(y_values), len(x_values)), np.nan)
                
                for i, y_val in enumerate(y_values):
                    for j, x_val in enumerate(x_values):
                        submask = (panel_df[y_param] == y_val) & (panel_df[x_param] == x_val)
                        if submask.any():
                            matrix[i, j] = panel_df[submask]['score'].mean()
                
                # Plot heatmap
                im = ax.imshow(matrix, cmap=cmap, norm=norm, aspect='auto', origin='lower')
                
                # Set ticks and labels
                ax.set_xticks(range(len(x_values)))
                ax.set_xticklabels([f'{v:.2f}' for v in x_values], fontsize=8, rotation=45)
                ax.set_yticks(range(len(y_values)))
                ax.set_yticklabels([f'{v:.2f}' for v in y_values], fontsize=8)
                
                # Labels only on edges
                if col_idx == 0:
                    ax.set_ylabel(y_param, fontsize=10)
                if row_idx == n_rows - 1:
                    ax.set_xlabel(x_param, fontsize=10)
                
                # Title with panel parameters
                ax.set_title(f'{col_param}={col_val:.3f}', fontsize=11, pad=5)
                
                # Add row label on the left
                if col_idx == 0:
                    ax.text(-0.5, 0.5, f'{row_param}={row_val:.3f}', 
                           transform=ax.transAxes, fontsize=10, 
                           ha='right', va='center', rotation=90)
        
        # Add colorbar
        fig.colorbar(ScalarMappable(norm=norm, cmap=cmap), ax=axes.ravel().tolist(), 
                    label='Score (%)', pad=0.02, fraction=0.046)
        
        # Main title
        fig.suptitle(f'4D GridSearch: {y_param} vs {x_param}\nRows: {row_param} | Columns: {col_param}', 
                    fontsize=14, y=0.995)
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        print(f"\n✅ 4D Heatmap saved to {output_file}")
        plt.close()

    def create_heatmaps(self, output_file='heatmap_gridsearch_2d.png'):
        """
        Create 2D heatmap for fertility_multiplier vs mortality_multiplier using matplotlib.
        
        Args:
            output_file: Name of the output PNG file
        """
        if not self.results:
            print("No results to visualize. Run optimize() first.")
            return
        
        # Convert results to DataFrame
        df = pd.DataFrame(self.results)
        
        param1 = 'fertility_multiplier'
        param2 = 'mortality_multiplier'
        
        # Get unique values for the two parameters
        x_values = sorted(df[param2].unique())
        y_values = sorted(df[param1].unique())
        
        # Create matrix
        matrix = np.full((len(y_values), len(x_values)), np.nan)
        
        for i, y_val in enumerate(y_values):
            for j, x_val in enumerate(x_values):
                mask = (df[param1] == y_val) & (df[param2] == x_val)
                if mask.any():
                    # Average score if multiple values
                    matrix[i, j] = df[mask]['score'].mean()
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Get min/max for normalization
        z_min = np.nanmin(matrix)
        z_max = np.nanmax(matrix)
        norm = Normalize(vmin=z_min, vmax=z_max)
        
        # Plot heatmap
        im = ax.imshow(matrix, cmap='RdYlGn_r', norm=norm, aspect='auto', origin='lower')
        
        # Set ticks
        ax.set_xticks(range(len(x_values)))
        ax.set_xticklabels([f'{v:.2f}' for v in x_values], rotation=45)
        ax.set_yticks(range(len(y_values)))
        ax.set_yticklabels([f'{v:.2f}' for v in y_values])
        
        # Labels
        ax.set_xlabel(param2, fontsize=12)
        ax.set_ylabel(param1, fontsize=12)
        ax.set_title('GridSearch Parameter Optimization - 2D Heatmap\nProcentowa zmiana populacji dla kombinacji parametrów', 
                    fontsize=14, pad=15)
        
        # Add colorbar
        cbar = fig.colorbar(im, ax=ax, label='Score (%)')
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        print(f"\n✅ 2D Heatmap saved to {output_file}")
        plt.close()


def create_parameter_grid():
    """
    Create 4D parameter grid for optimization with balanced complexity.
    
    fertility_multiplier & mortality_multiplier: Main heatmap parameters (X, Y axes) - 4 levels
    birth_rate_factor & death_rate_factor: Panel organization parameters (rows, columns) - 5 levels each
    
    Total combinations: 4 × 4 × 5 × 5 = 400 parameter sets per iteration
    """
    return {
        # Main heatmap dimensions - fertility and mortality multipliers
        "fertility_multiplier": [0.5, 1.0, 1.5, 2.0],  # 4 values - X axis of heatmaps
        "mortality_multiplier": [0.5, 1.0, 1.5, 2.0],  # 4 values - Y axis of heatmaps
        
        # Panel organization dimensions - optimized for speed and detail
        "birth_rate_factor": list(np.linspace(0.7, 1.3, 5)),  # 5 values - rows (0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3)
        "death_rate_factor": list(np.linspace(0.6, 1.4, 5)),  # 5 values - columns (0.6, 0.8, 1.0, 1.2, 1.4)
    }


def simulation_scoring_function(fertility_multiplier, mortality_multiplier, birth_rate_factor, death_rate_factor):
    """
    Scoring function for 4D simulation parameters using full ABM model.
    
    Parameters:
        fertility_multiplier: Multiplier for fertility rate
        mortality_multiplier: Multiplier for mortality rate  
        birth_rate_factor: Scaling factor for birth rate table (demographic scenario)
        death_rate_factor: Scaling factor for death rate table (demographic scenario)
    
    Returns:
        Population growth score (percentage change from initial population)
    """
    try:
        # Initialize disease model
        disease_model = DiseaseModel()
        
        # Create simulation engine with given parameters
        engine = SimulationEngine(disease_model=disease_model, seed=42)
        
        # Apply multipliers to demographic tables for different scenarios
        # This creates different baseline demographic conditions
        scaled_fertility_table = {
            age: rate * birth_rate_factor 
            for age, rate in engine.DEFAULT_FERTILITY_TABLE.items()
        }
        scaled_mortality_table = {
            age: (male_rate * death_rate_factor, female_rate * death_rate_factor)
            for age, (male_rate, female_rate) in engine.DEFAULT_MORTALITY_TABLE.items()
        }
        
        # Set the scaled tables
        engine.fertility_table = scaled_fertility_table
        engine.mortality_table = scaled_mortality_table
        
        # Main population dynamics parameters - the optimization variables
        engine.fertility_rate = fertility_multiplier
        engine.mortality_multiplier = mortality_multiplier
        engine.household_split_probability = 0.001
        
        # Generate small synthetic population (reduce time)
        engine._create_synthetic_population(1000)  # Smaller population for speed
        
        # Run simulation for 10 years (shorter for grid search)
        engine.run(months=120)  # 10 years
        
        # Calculate score: final population as percentage of initial
        initial_pop = 1000
        final_pop = len([c for c in engine.citizens.values() if c.alive])
        score = ((final_pop - initial_pop) / initial_pop) * 100
        
        return score
    except Exception as e:
        print(f"Error in simulation: {e}")
        return -1000  # Penalize errors


if __name__ == "__main__":
    print("=" * 80)
    print("GRIDSEARCH OPTIMIZATION WITH 4D HEATMAP VISUALIZATION")
    print("=" * 80)
    print()
    
    param_grid = create_parameter_grid()
    
    # Print parameter grid info
    print("Parameter Grid Configuration:")
    for param, values in param_grid.items():
        print(f"  {param}: {values} ({len(values)} levels)")
    total_combinations = np.prod([len(v) for v in param_grid.values()])
    print(f"  Total combinations to test: {total_combinations}")
    print()
    
    optimizer = GridSearchWithHeatmap(
        param_grid=param_grid,
        scoring_function=simulation_scoring_function,
        n_iter=2
    )
    
    # Run optimization
    best_params, best_score = optimizer.optimize()
    print()
    
    # Create visualizations
    print("\nGenerating visualizations...")
    optimizer.create_4d_heatmaps('heatmap_gridsearch_4d.png')
    optimizer.create_heatmaps('heatmap_gridsearch_2d.png')  # Also create 2D version for reference
    
    print("\n" + "=" * 80)
    print("VISUALIZATION COMPLETE")
    print("=" * 80)

