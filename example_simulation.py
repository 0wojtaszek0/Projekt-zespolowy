"""
Example: URBAN-ABM Demographic Simulation

This script demonstrates how to:
1. Set up zones and initial population
2. Run a 10-year demographic simulation
3. Collect and visualize statistics
"""

from demographic_engine import (
    SimulationEngine, Zone, DemographicTables,
    create_initial_population
)
import random

def main():
    """Run example demographic simulation."""
    
    print("="*60)
    print("URBAN-ABM: Demographic Population Engine")
    print("="*60)
    
    # Set random seed for reproducibility
    random.seed(42)
    
    # ========================================================================
    # SETUP: Create zones and simulation engine
    # ========================================================================
    
    print("\n[1] Setting up zones and simulation engine...")
    
    # Create 3 zones (districts)
    zones = [
        Zone(id=1),
        Zone(id=2),
        Zone(id=3)
    ]
    
    # Add environmental parameters (placeholder for future use)
    zones[0].set_param("density", "high")
    zones[0].set_param("development", "urban")
    zones[1].set_param("density", "medium")
    zones[1].set_param("development", "suburban")
    zones[2].set_param("density", "low")
    zones[2].set_param("development", "rural")
    
    # Create simulation engine
    engine = SimulationEngine(zones=zones)
    
    print(f"   Created {len(zones)} zones")
    print(f"   Zones: {[z.id for z in zones]}")
    
    # ========================================================================
    # POPULATION: Initialize with 10,000 people
    # ========================================================================
    
    print("\n[2] Creating initial population...")
    
    initial_pop = 10000
    create_initial_population(
        engine=engine,
        zone_ids=[z.id for z in zones],
        initial_population=initial_pop,
        age_distribution="realistic"
    )
    # load_agents_from_data(engine, "initial_population.csv")  # Alternative: load from CSV
    
    living = [c for c in engine.citizens.values() if c.alive]
    print(f"   Initial population: {len(living)} citizens")
    print(f"   Households created: {len([h for h in engine.households.values() if h.get_size() > 0])}")
    
    stats = engine.get_population_stats()
    print(f"   Males: {stats['num_living_males']}, Females: {stats['num_living_females']}")
    print(f"   Average household size: {stats['average_household_size']:.2f}")
    
    # ========================================================================
    # SIMULATION: Run for 10 years (120 months)
    # ========================================================================
    
    print("\n[3] Running simulation for 10 years...")
    
    simulation_months = 10 * 12  # 10 years
    engine.run(simulation_months)
    
    print(f"   Simulation complete!")
    print(f"   Simulated time: {engine.current_month} months ({engine.current_month / 12:.1f} years)")
    
    # ========================================================================
    # RESULTS: Display yearly statistics
    # ========================================================================
    
    print("\n[4] Population Statistics by Year:")
    print("-" * 70)
    print(f"{'Year':<6} {'Population':<15} {'Households':<15} {'Avg HH Size':<15}")
    print("-" * 70)
    
    for year in sorted(engine.yearly_stats.keys()):
        stats = engine.yearly_stats[year]
        print(f"{year:<6} {stats['total_population']:<15} {stats['num_households']:<15} "
              f"{stats['average_household_size']:<15.2f}")
    
    # ========================================================================
    # FINAL STATUS
    # ========================================================================
    
    print("\n[5] Final Population Status:")
    final_stats = engine.get_population_stats()
    print(f"   Total population: {final_stats['total_population']}")
    print(f"   Number of households: {final_stats['num_households']}")
    print(f"   Average household size: {final_stats['average_household_size']:.2f}")
    print(f"   Males: {final_stats['num_living_males']}")
    print(f"   Females: {final_stats['num_living_females']}")
    
    # ========================================================================
    # VISUALIZATION
    # ========================================================================
    
    print("\n[6] Generating visualizations...")
    print("   Opening plots... (close each plot to continue)")
    
    # Plot 1: Population over time
    engine.plot_population_over_time()
    
    # Plot 2: Households over time
    engine.plot_households_over_time()
    
    # Plot 3: Age pyramid for final year
    final_year = max(engine.yearly_stats.keys())
    engine.plot_age_pyramid(year=final_year)
    
    print("\n" + "="*60)
    print("Simulation completed successfully!")
    print("="*60)


if __name__ == "__main__":
    main()