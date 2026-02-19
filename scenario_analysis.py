"""
Example script demonstrating parameter tuning for the ABM simulation.
Shows how to modify simulation parameters and run different scenarios.
"""

from simulation_engine import SimulationEngine
from disease_model import DiseaseModel
from visualization import SimulationVisualizer


def scenario_baseline() -> None:
    """Run baseline scenario with default parameters."""
    print("\n" + "="*70)
    print("SCENARIO 1: BASELINE (Default parameters)")
    print("="*70)
    
    engine = SimulationEngine(seed=42)
    engine.fertility_rate = 1.0
    engine.mortality_multiplier = 1.0
    engine.household_split_probability = 0.001
    
    print("Parameters:")
    print(f"  Fertility rate: {engine.fertility_rate}")
    print(f"  Mortality multiplier: {engine.mortality_multiplier}")
    print(f"  Household split probability: {engine.household_split_probability}")
    
    loaded = engine._create_synthetic_population(1600)
    print(f"  Initial population: {loaded}")
    
    engine.run(months=600)
    print(engine.get_statistics_summary())
    
    visualizer = SimulationVisualizer(engine.yearly_stats)
    visualizer.generate_all_plots()


def scenario_higher_fertility() -> None:
    """Run scenario with higher fertility rate."""
    print("\n" + "="*70)
    print("SCENARIO 2: HIGHER FERTILITY (fertility_rate = 1.5)")
    print("="*70)
    
    engine = SimulationEngine(seed=42)
    engine.fertility_rate = 1.5  # 50% higher fertility
    engine.mortality_multiplier = 1.0
    engine.household_split_probability = 0.001
    
    print("Parameters:")
    print(f"  Fertility rate: {engine.fertility_rate}")
    print(f"  Mortality multiplier: {engine.mortality_multiplier}")
    
    loaded = engine._create_synthetic_population(1600)
    print(f"  Initial population: {loaded}")
    
    engine.run(months=600)
    print(engine.get_statistics_summary())


def scenario_lower_mortality() -> None:
    """Run scenario with lower mortality rate."""
    print("\n" + "="*70)
    print("SCENARIO 3: LOWER MORTALITY (mortality_multiplier = 0.5)")
    print("="*70)
    
    engine = SimulationEngine(seed=42)
    engine.fertility_rate = 1.0
    engine.mortality_multiplier = 0.5  # 50% lower mortality
    engine.household_split_probability = 0.001
    
    print("Parameters:")
    print(f"  Fertility rate: {engine.fertility_rate}")
    print(f"  Mortality multiplier: {engine.mortality_multiplier}")
    
    loaded = engine._create_synthetic_population(1600)
    print(f"  Initial population: {loaded}")
    
    engine.run(months=600)
    print(engine.get_statistics_summary())


def scenario_high_migration() -> None:
    """Run scenario with higher household split rate (migration)."""
    print("\n" + "="*70)
    print("SCENARIO 4: HIGH MIGRATION (household_split_probability = 0.005)")
    print("="*70)
    
    engine = SimulationEngine(seed=42)
    engine.fertility_rate = 1.0
    engine.mortality_multiplier = 1.0
    engine.household_split_probability = 0.005  # 0.5% monthly
    
    print("Parameters:")
    print(f"  Fertility rate: {engine.fertility_rate}")
    print(f"  Mortality multiplier: {engine.mortality_multiplier}")
    print(f"  Household split probability: {engine.household_split_probability}")
    
    loaded = engine._create_synthetic_population(1600)
    print(f"  Initial population: {loaded}")
    
    engine.run(months=600)
    print(engine.get_statistics_summary())


if __name__ == "__main__":
    print("=" * 70)
    print("SCENARIO ANALYSIS - Urban Health ABM")
    print("=" * 70)
    print("\nThis script demonstrates how to modify simulation parameters")
    print("and analyze different demographic scenarios.")
    print("\nNote: Modify the commented out lines below to run specific scenarios.")
    
    # Uncomment to run different scenarios:
    
    # scenario_baseline()              # Default parameters
    # scenario_higher_fertility()      # Increased fertility
    # scenario_lower_mortality()       # Decreased mortality
    # scenario_high_migration()        # Increased household splitting
    
    print("\n" + "="*70)
    print("To run a scenario, uncomment the function call at the bottom")
    print("of this file and run: python scenario_analysis.py")
    print("="*70)
