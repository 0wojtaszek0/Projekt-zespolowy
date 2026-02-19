"""
Main entry point for the Urban Health ABM simulation.

This script orchestrates the entire simulation:
1. Loads initial population from Excel file
2. Runs 50-year (600-month) demographic simulation
3. Collects yearly statistics
4. Generates interactive visualizations
"""

import sys
from simulation_engine import SimulationEngine
from disease_model import DiseaseModel
from visualization import SimulationVisualizer


def main() -> None:
    """Main simulation execution function."""
    
    print("=" * 70)
    print("URBAN HEALTH AGENT-BASED MODEL (ABM)")
    print("Population Demographics & Multimorbidity Simulation")
    print("=" * 70)
    print()
    
    # Initialize disease model with top 15 diseases
    print("Initializing disease model...")
    disease_model = DiseaseModel()
    print(f"Selected {disease_model.get_disease_count()} diseases for simulation:")
    for i, disease in enumerate(disease_model.diseases, 1):
        prevalence = disease_model.get_prevalence(disease)
        weight = disease_model.get_disability_weight(disease)
        print(f"  {i:2}. {disease:<40} (prevalence={prevalence:5.1f}%, disability={weight:.2f})")
    print()
    
    # Create simulation engine
    print("Creating simulation engine...")
    engine = SimulationEngine(
        disease_model=disease_model,
        seed=42,  # For reproducibility
    )
    
    # Configure simulation parameters
    engine.fertility_rate = 1.0
    engine.mortality_multiplier = 1.0
    engine.household_split_probability = 0.001
    
    print(f"  Fertility rate: {engine.fertility_rate}")
    print(f"  Mortality multiplier: {engine.mortality_multiplier}")
    print(f"  Household split probability: {engine.household_split_probability}")
    print()
    
    # Load initial population
    print("Loading initial population...")
    try:
        loaded = engine.load_initial_population("population_data.xlsx")
        print(f"  Loaded {loaded} citizens from population_data.xlsx")
    except Exception as e:
        print(f"  Info: {e}")
        loaded = engine._create_synthetic_population(1600)
        print(f"  Created {loaded} citizens (synthetic)")
    
    print(f"  Initial households: {len(engine.households)}")
    print()
    
    # Run simulation
    print("Running simulation for 50 years (600 months)...")
    engine.run(months=600)
    print()
    
    # Display final statistics
    print(engine.get_statistics_summary())
    print()
    
    # Generate visualizations
    print("Generating interactive visualizations...")
    visualizer = SimulationVisualizer(engine.yearly_stats)
    visualizer.generate_all_plots()
    print()
    
    print("=" * 70)
    print("SIMULATION COMPLETE")
    print("=" * 70)
    print("\nGenerated files:")
    print("  - age_pyramid_interactive.html (Age pyramid with year slider)")
    print("  - population_trends.html (Population, multimorbidity, disability trends)")
    print("  - households_trends.html (Household dynamics)")
    print("  - gender_distribution.html (Male/female distribution)")
    print("\nOpen these HTML files in a web browser to interact with the visualizations.")
    print()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
