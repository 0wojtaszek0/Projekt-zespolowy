"""
Example: URBAN-ABM Demographic Simulation (No Visualization)

This script demonstrates the core functionality without plots.
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
    print("-" * 80)
    print(f"{'Year':<6} {'Population':<15} {'Households':<15} {'Avg HH Size':<15} {'HH w/ Children':<15}")
    print("-" * 80)
    
    for year in sorted(engine.yearly_stats.keys()):
        stats = engine.yearly_stats[year]
        print(f"{year:<6} {stats['total_population']:<15} {stats['num_households']:<15} "
              f"{stats['average_household_size']:<15.2f} {stats['num_households_with_children']:<15}")
    
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
    # AGE PYRAMID
    # ========================================================================
    
    print("\n[6] Final Year Age Pyramid:")
    final_year = max(engine.yearly_stats.keys())
    pyramid = engine.yearly_stats[final_year]['age_pyramid']
    
    age_bins = [f"{i}-{i+4}" for i in range(0, 85, 5)] + ["85+"]
    
    print("-" * 70)
    print(f"{'Age Group':<15} {'Male':<15} {'Female':<15} {'Total':<15}")
    print("-" * 70)
    
    for bin_label in age_bins:
        males = pyramid['male'].get(bin_label, 0)
        females = pyramid['female'].get(bin_label, 0)
        total = males + females
        print(f"{bin_label:<15} {males:<15} {females:<15} {total:<15}")
    
    print("-" * 70)
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    
    print("\n[7] Simulation Summary:")
    years_recorded = sorted(engine.yearly_stats.keys())
    if len(years_recorded) > 0:
        initial_pop_actual = engine.yearly_stats[years_recorded[0]]['total_population']
        final_year = years_recorded[-1]
        final_pop = engine.yearly_stats[final_year]['total_population']
        pop_change = final_pop - initial_pop_actual
        pop_change_pct = (pop_change / initial_pop_actual * 100) if initial_pop_actual > 0 else 0
        
        print(f"   Initial population (Year {years_recorded[0]}): {initial_pop_actual}")
        print(f"   Final population (Year {final_year}): {final_pop}")
        print(f"   Change: {pop_change} ({pop_change_pct:+.2f}%)")
        print(f"   Simulation duration: {engine.current_month} months")
    
    print("\n" + "="*60)
    print("Simulation completed successfully!")
    print("="*60)


if __name__ == "__main__":
    main()
