# URBAN-ABM: Urban Agent-Based Model - Demographic Engine

A comprehensive object-oriented demographic population engine for agent-based modeling in Python.

## Overview

**URBAN-ABM** provides a foundation for urban demographic simulations with:

- **Entity-Based Architecture**: Citizens, Households, and Zones as distinct OOP classes
- **Realistic Demographic Processes**: Age/sex-dependent mortality, fertility, and household dynamics
- **Statistical Tracking**: Yearly statistics collection with visualization
- **Extensible Design**: Clean separation of concerns for easy integration with health/economic modules

## Architecture

### Core Entities

#### Citizen
Represents an individual with:
- `id`: Unique identifier
- `sex`: "M" or "F"
- `age_months`: Age in months (float internally for precision)
- `age_years`: Computed property (age_months / 12)
- `alive`: Boolean flag
- `household_id`: Reference to household
- `zone_id`: Reference to zone

#### Household
Contains multiple citizens:
- `id`: Unique identifier
- `zone_id`: Zone reference
- `members`: List of Citizen objects
- Methods: add_member(), remove_member(), get_living_members(), get_size()

#### Zone
Represents spatial district with:
- `id`: Unique identifier
- `environmental_params`: Dict for future extensibility (health risks, etc.)

#### SimulationEngine
Main orchestrator managing:
- Citizen and household creation
- Simulation time stepping
- Demographic processes (aging, mortality, fertility, household formation)
- Statistics collection and visualization

### Demographic Tables

The `DemographicTables` class provides:

**Mortality Rates** (per 1000 per year, by age group and sex):
- Realistic values from standard demographic tables
- Age groups: 0-1, 1-5, 5-10, ..., 75-80, 80+
- Sex-specific rates (Males generally higher)

**Fertility Rates** (births per woman per year):
- Ages 15-20: 0.05, 20-25: 0.15, 25-30: 0.20 (peak), etc.
- Ages 15-49 (0 outside this range)

**Household Formation**:
- Citizens age ≥25 can form households
- Monthly probability: 5% (tunable)

## Simulation Loop (Per Month)

1. **Aging**: All living citizens age by 1 month
2. **Mortality**: Kill citizens based on age/sex-dependent probabilistic rates
3. **Fertility**: Create newborns for eligible females
4. **Household Formation**: Move eligible citizens to new households

### Time Conversion

Demographic rates are provided as annual probabilities, converted to monthly:
```python
monthly_prob = 1.0 - (1.0 - annual_rate)^(1/12)   # Mortality
monthly_prob = annual_rate / 12                    # Fertility
```

## Statistics & Visualization

### Collection (Yearly)

At the end of each year, the engine collects:
- Total population
- Age pyramid (5-year bins, separated by sex)
- Number of households
- Average household size

### Visualization Methods

```python
engine.plot_population_over_time()      # Line plot of population
engine.plot_households_over_time()      # Dual-axis: households + avg size
engine.plot_age_pyramid(year=2030)      # Age pyramid for specific year
```

## Usage

### Basic Setup

```python
from demographic_engine import SimulationEngine, Zone, create_initial_population

# Create zones
zones = [Zone(id=1), Zone(id=2), Zone(id=3)]

# Initialize engine
engine = SimulationEngine(zones=zones)

# Create initial population
create_initial_population(
    engine=engine,
    zone_ids=[1, 2, 3],
    initial_population=10000,
    age_distribution="realistic"
)

# Run simulation
engine.run(months=120)  # 10 years

# Visualize
engine.plot_population_over_time()
engine.plot_age_pyramid(year=10)
```

### Custom Demographics

```python
# Define custom tables
custom_mortality = {
    "M": [7.0, 0.9, 0.5, ...],
    "F": [6.0, 0.8, 0.4, ...]
}

custom_fertility = [0.08, 0.18, 0.22, ...]

# Pass to engine
engine = SimulationEngine(
    zones=zones,
    mortality_table=custom_mortality,
    fertility_table=custom_fertility
)
```

### Accessing Data

```python
# Get current stats
stats = engine.get_population_stats()
print(f"Population: {stats['total_population']}")
print(f"Households: {stats['num_households']}")

# Get yearly history
for year in sorted(engine.yearly_stats.keys()):
    data = engine.yearly_stats[year]
    print(f"Year {year}: {data['total_population']} people")
    print(f"  Age pyramid: {data['age_pyramid']}")
```

### Manual Population Management

```python
# Add individual citizen
citizen = engine.add_citizen(
    sex="F",
    age_months=240,    # 20 years
    zone_id=1,
    household_id=5
)

# Create household
household = engine.create_household(zone_id=2)

# Single step
engine.step()  # One month simulation

# Multiple steps
engine.run(months=12)  # Run 12 more months
```

## Design Principles

1. **Separation of Concerns**: Demographic logic independent from health/economic modules
2. **Parameterization**: All rates passed as tables, not hardcoded
3. **Probabilistic**: Realistic stochastic processes
4. **Extensibility**: Zone environmental params for future integration
5. **Stateless Tables**: `DemographicTables` as utility class for rate lookups
6. **Monthly Time Step**: Flexible enough for real-time updates

## Files

- `demographic_engine.py`: Core engine implementation
- `example_simulation.py`: Example 10-year simulation with visualization
- `README.md`: This file

## Dependencies

- `numpy`: Numerical operations
- `matplotlib`: Visualization
- Standard library: `random`, `dataclasses`, `collections`, `typing`

## Running Examples

```bash
python example_simulation.py
```

This will:
1. Create 3 zones
2. Initialize 10,000 citizens
3. Run a 10-year simulation
4. Display yearly statistics
5. Generate 3 plots (population, households, age pyramid)

## Future Extensions

The modular design allows easy integration of:

- **Health Module**: Attach disease risks to zones/demographics
- **Economic Module**: Income, employment, consumption
- **Migration Module**: Movement between zones
- **Spatial Module**: Explicit geospatial data structures
- **Policy Module**: Interventions (tax, healthcare, etc.)

Each module can access entity data without modifying core demographic logic.

## License

Use freely for research and educational purposes.
