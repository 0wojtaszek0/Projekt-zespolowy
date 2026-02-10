"""
Advanced Usage Examples for URBAN-ABM Demographic Engine

Demonstrates:
- Custom demographic parameters
- Multiple zone scenarios
- Data extraction and analysis
- Extended statistics tracking
"""

from demographic_engine import (
    SimulationEngine, Zone, DemographicTables,
    create_initial_population
)
import random


# ==============================================================================
# Example 1: Custom Mortality Rates (Developing Country Scenario)
# ==============================================================================

def example_high_mortality():
    """
    Simulate a developing country with higher infant mortality
    and life expectancy of ~60 years.
    """
    print("\n" + "="*70)
    print("EXAMPLE 1: High Mortality Scenario (Developing Country)")
    print("="*70)
    
    # Custom higher mortality rates (per 1000)
    high_mortality = {
        "M": [25.0, 4.0, 1.5, 1.2, 2.0, 2.5, 3.0, 3.5, 4.5, 
              6.0, 8.5, 12.0, 18.0, 27.0, 40.0, 60.0, 90.0, 150.0],
        "F": [20.0, 3.5, 1.3, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 
              5.5, 7.5, 10.0, 15.0, 22.0, 33.0, 50.0, 75.0, 130.0]
    }
    
    zones = [Zone(id=1)]
    engine = SimulationEngine(zones=zones, mortality_table=high_mortality)
    
    create_initial_population(
        engine=engine,
        zone_ids=[1],
        initial_population=5000,
        age_distribution="realistic"
    )
    
    print(f"Initial population: {len([c for c in engine.citizens.values() if c.alive])}")
    
    # Run for 5 years
    engine.run(months=60)
    
    final_pop = engine.yearly_stats[5]['total_population']
    print(f"Final population (year 5): {final_pop}")
    print(f"Population change: {final_pop - engine.yearly_stats[1]['total_population']}")


# ==============================================================================
# Example 2: Custom Fertility Rates (High Fertility Scenario)
# ==============================================================================

def example_high_fertility():
    """
    Simulate a high-fertility population with average of 5+ children per woman.
    """
    print("\n" + "="*70)
    print("EXAMPLE 2: High Fertility Scenario")
    print("="*70)
    
    # Custom higher fertility rates
    high_fertility = [0.15, 0.25, 0.30, 0.28, 0.20, 0.10, 0.03]
    
    zones = [Zone(id=1)]
    engine = SimulationEngine(zones=zones, fertility_table=high_fertility)
    
    create_initial_population(
        engine=engine,
        zone_ids=[1],
        initial_population=5000,
        age_distribution="realistic"
    )
    
    print(f"Initial population: {len([c for c in engine.citizens.values() if c.alive])}")
    
    # Run for 10 years
    engine.run(months=120)
    
    final_pop = engine.yearly_stats[10]['total_population']
    print(f"Final population (year 10): {final_pop}")
    print(f"Population change: {final_pop - engine.yearly_stats[1]['total_population']}")


# ==============================================================================
# Example 3: Multi-Zone Migration Tracking
# ==============================================================================

def example_multi_zone_analysis():
    """
    Simulate multiple zones and track zone-level demographics.
    """
    print("\n" + "="*70)
    print("EXAMPLE 3: Multi-Zone Population Tracking")
    print("="*70)
    
    # Create 3 zones with different characteristics
    zones = [
        Zone(id=1),  # Urban
        Zone(id=2),  # Suburban
        Zone(id=3)   # Rural
    ]
    
    zones[0].set_param("type", "urban")
    zones[1].set_param("type", "suburban")
    zones[2].set_param("type", "rural")
    
    engine = SimulationEngine(zones=zones)
    
    # Initialize with equal distribution
    create_initial_population(
        engine=engine,
        zone_ids=[1, 2, 3],
        initial_population=9000,  # 3000 per zone
        age_distribution="realistic"
    )
    
    # Run simulation
    engine.run(months=120)
    
    # Analyze zone populations
    print("\nZone Population Distribution (Year 10):")
    print("-" * 50)
    
    for zone_id in [1, 2, 3]:
        zone_citizens = [c for c in engine.citizens.values() 
                        if c.alive and c.zone_id == zone_id]
        zone_name = zones[zone_id-1].get_param("type")
        print(f"Zone {zone_id} ({zone_name}): {len(zone_citizens)} citizens")


# ==============================================================================
# Example 4: Extract and Analyze Age Structure
# ==============================================================================

def example_age_structure_analysis():
    """
    Extract detailed age structure analysis.
    """
    print("\n" + "="*70)
    print("EXAMPLE 4: Age Structure Analysis")
    print("="*70)
    
    zones = [Zone(id=1)]
    engine = SimulationEngine(zones=zones)
    
    create_initial_population(
        engine=engine,
        zone_ids=[1],
        initial_population=10000,
        age_distribution="realistic"
    )
    
    # Run simulation
    engine.run(months=120)
    
    final_year = max(engine.yearly_stats.keys())
    pyramid = engine.yearly_stats[final_year]['age_pyramid']
    
    # Calculate age structure indicators
    total_pop = engine.yearly_stats[final_year]['total_population']
    
    # Children (0-14)
    children = sum(v for k, v in pyramid['male'].items() if k.split('-')[0].isdigit() and int(k.split('-')[0]) < 15)
    children += sum(v for k, v in pyramid['female'].items() if k.split('-')[0].isdigit() and int(k.split('-')[0]) < 15)
    
    # Working age (15-64)
    working = sum(v for k, v in pyramid['male'].items() if k.split('-')[0].isdigit() 
                 and 15 <= int(k.split('-')[0]) < 65)
    working += sum(v for k, v in pyramid['female'].items() if k.split('-')[0].isdigit() 
                  and 15 <= int(k.split('-')[0]) < 65)
    
    # Elderly (65+)
    elderly = sum(v for k, v in pyramid['male'].items() if k.split('-')[0].isdigit() and int(k.split('-')[0]) >= 65)
    elderly += sum(v for k, v in pyramid['female'].items() if k.split('-')[0].isdigit() and int(k.split('-')[0]) >= 65)
    
    print(f"\nAge Structure (Year {final_year}):")
    print(f"  Total population: {total_pop}")
    print(f"  Children (0-14): {children} ({100*children/total_pop:.1f}%)")
    print(f"  Working age (15-64): {working} ({100*working/total_pop:.1f}%)")
    print(f"  Elderly (65+): {elderly} ({100*elderly/total_pop:.1f}%)")
    print(f"\n  Dependency ratio: {100*(children+elderly)/working:.2f}")
    print(f"  Sex ratio (M/F): {pyramid['male'].get('50-54', 1)/max(1, pyramid['female'].get('50-54', 1)):.2f}")


# ==============================================================================
# Example 5: Household Composition Analysis
# ==============================================================================

def example_household_analysis():
    """
    Analyze household structure evolution.
    """
    print("\n" + "="*70)
    print("EXAMPLE 5: Household Composition Analysis")
    print("="*70)
    
    zones = [Zone(id=1)]
    engine = SimulationEngine(zones=zones)
    
    create_initial_population(
        engine=engine,
        zone_ids=[1],
        initial_population=10000,
        age_distribution="realistic"
    )
    
    # Run simulation
    engine.run(months=120)
    
    print("\nHousehold Statistics by Year:")
    print("-" * 60)
    print(f"{'Year':<6} {'Total HH':<12} {'Avg Size':<12} {'With Children':<15}")
    print("-" * 60)
    
    for year in sorted(engine.yearly_stats.keys()):
        stats = engine.yearly_stats[year]
        print(f"{year:<6} {stats['num_households']:<12} "
              f"{stats['average_household_size']:<12.2f} "
              f"{stats['num_households_with_children']:<15}")


# ==============================================================================
# Main execution
# ==============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("URBAN-ABM: Advanced Usage Examples")
    print("="*70)
    
    random.seed(42)  # For reproducibility
    
    # Run examples
    example_high_mortality()
    example_high_fertility()
    example_multi_zone_analysis()
    example_age_structure_analysis()
    example_household_analysis()
    
    print("\n" + "="*70)
    print("All examples completed successfully!")
    print("="*70)
