from sklearn.model_selection import ParameterGrid
import numpy as np

class GridSearchOptimization:
    def __init__(self, param_grid, scoring_function, n_iter=50):
        """
        param_grid: Dictionary of parameters to optimize.
        scoring_function: Function to evaluate the simulation.
        n_iter: Number of iterations to repeat the GridSearch for stability.
        """
        self.param_grid = param_grid
        self.scoring_function = scoring_function
        self.n_iter = n_iter

    def optimize(self):
        """
        Perform GridSearch to find the best parameters with enhanced complexity.
        """
        best_params = None
        best_score = -float('inf')

        for i in range(self.n_iter):
            print(f"Iteration {i + 1}/{self.n_iter}")
            for params in ParameterGrid(self.param_grid):
                # Add additional logic to refine parameter selection
                if params['birth_rate'] < params['mortality_rate']:
                    continue  # Skip invalid parameter combinations

                score = self.scoring_function(**params)
                if score > best_score:
                    best_score = score
                    best_params = params

        print("Final best parameters:", best_params)
        print("Final best score:", best_score)
        return best_params, best_score

# Example usage
if __name__ == "__main__":
    def simulation_scoring_function(birth_rate, mortality_rate, fertility_multiplier, mortality_multiplier, migration_rate):
        # Updated scoring logic to ensure final population is significantly greater than half the initial population
        def run_simulation(birth_rate, mortality_rate, fertility_multiplier, mortality_multiplier, migration_rate):
            # Improved simulation logic to better reflect population dynamics
            initial_population = 50000
            final_population = initial_population

            for year in range(50):
                births = final_population * birth_rate * fertility_multiplier
                deaths = final_population * mortality_rate * mortality_multiplier
                migration = initial_population * migration_rate  # Migration based on initial population
                final_population += births - deaths + migration

                # Ensure population does not drop below zero
                if final_population < 0:
                    final_population = 0
                    break

            return final_population

        final_population = run_simulation(birth_rate, mortality_rate, fertility_multiplier, mortality_multiplier, migration_rate)
        target_population = 30000  # Significantly greater than half of the initial population
        score = final_population - target_population  # Positive score if above target
        return score

    param_grid = {
        "birth_rate": [0.02 + i * 0.001 for i in range(10)],  # Narrowed range for birth_rate
        "mortality_rate": [0.001 + i * 0.0001 for i in range(10)],  # Narrowed range for mortality_rate
        "fertility_multiplier": [0.8 + i * 0.1 for i in range(5)],  # Narrowed range for fertility multiplier
        "mortality_multiplier": [0.7 + i * 0.1 for i in range(5)],  # Narrowed range for mortality multiplier
        "migration_rate": [-0.01 + i * 0.001 for i in range(10)]  # Narrowed range for migration
    }

    optimizer = GridSearchOptimization(param_grid, scoring_function=simulation_scoring_function, n_iter=10)
    optimizer.optimize()