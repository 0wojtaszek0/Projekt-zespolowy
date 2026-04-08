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
    def simulation_scoring_function(birth_rate, mortality_rate, fertility_multiplier, mortality_multiplier):
        # Scoring function for 4D GridSearch (without migration)
        # Simplified model focusing on natural demographic processes
        def run_simulation(birth_rate, mortality_rate, fertility_multiplier, mortality_multiplier):
            # Simulation logic for closed population (no migration)
            initial_population = 50000
            final_population = initial_population

            for year in range(50):
                births = final_population * birth_rate * fertility_multiplier
                deaths = final_population * mortality_rate * mortality_multiplier
                final_population += births - deaths

                # Ensure population does not drop below zero
                if final_population < 0:
                    final_population = 0
                    break

            return final_population

        final_population = run_simulation(birth_rate, mortality_rate, fertility_multiplier, mortality_multiplier)
        target_population = 30000  # Target population after 50 years
        score = final_population - target_population  # Positive score if above target
        return score

    param_grid = {
        "birth_rate": [0.01 + i * 0.002 for i in range(25)],  # birth_rate range: 0.01 to 0.058
        "mortality_rate": [0.0005 + i * 0.0001 for i in range(25)],  # mortality_rate range: 0.0005 to 0.0025
        "fertility_multiplier": [0.5 + i * 0.2 for i in range(10)],  # fertility multiplier: 0.5 to 2.3
        "mortality_multiplier": [0.5 + i * 0.2 for i in range(10)],  # mortality multiplier: 0.5 to 2.3
    }

    optimizer = GridSearchOptimization(param_grid, scoring_function=simulation_scoring_function, n_iter=10)
    optimizer.optimize()