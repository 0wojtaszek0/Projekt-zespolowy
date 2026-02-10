# URBAN-ABM: Quick Start Guide

## Installation

1. **Install Python 3.7+** (if not already installed)

2. **Navigate to project directory:**
   ```bash
   cd /Users/wojciechofiara/Desktop/Studia/Projekt\ zespołowy/urban_abm
   ```

3. **Install dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

## Running Simulations

### Quick Test (No Visualization)
```bash
python3 test_simulation.py
```
This runs a 10-year simulation with 10,000 initial citizens across 3 zones.

### Example with Full Features
```bash
python3 example_simulation.py
```
Same as above but generates matplotlib visualizations (requires display).

### Advanced Examples
```bash
python3 advanced_examples.py
```
Demonstrates:
- Custom mortality rates (high mortality scenario)
- Custom fertility rates (high fertility scenario)
- Multi-zone analysis
- Age structure indicators
- Household composition trends

## Basic Usage in Your Own Code

```python
from demographic_engine import SimulationEngine, Zone, create_initial_population

# Create zones
zones = [Zone(id=1), Zone(id=2)]

# Create engine
engine = SimulationEngine(zones=zones)

# Initialize population (5000 people distributed across zones)
create_initial_population(
    engine=engine,
    zone_ids=[1, 2],
    initial_population=5000
)

# Run simulation for 5 years
engine.run(months=60)

# Get results
stats = engine.get_population_stats()
print(f"Final population: {stats['total_population']}")
print(f"Households: {stats['num_households']}")

# Access yearly statistics
for year in sorted(engine.yearly_stats.keys()):
    print(f"Year {year}: {engine.yearly_stats[year]['total_population']} people")
```

## Key Classes

### Citizen
```python
citizen = engine.add_citizen(
    sex="F",                # "M" or "F"
    age_months=240,         # Age in months
    zone_id=1,             # Which zone
    household_id=5         # Which household (optional)
)

# Properties
print(citizen.age_years)   # Age in years (computed)
print(citizen.alive)       # Boolean
```

### Household
```python
household = engine.create_household(zone_id=1)
household.add_member(citizen)
print(household.get_size())  # Number of living members
```

### Zone
```python
zone = Zone(id=1)
zone.set_param("density", "high")
zone.set_param("development_level", 0.8)
```

## Simulation Parameters

### Modifying Demographic Rates

```python
from demographic_engine import DemographicTables

# Custom mortality (per 1000 per year by age group)
custom_mortality = {
    "M": [10.0, 1.0, 0.5, ..., 100.0],  # 18 age groups
    "F": [9.0, 0.9, 0.4, ..., 90.0]
}

# Custom fertility (births per woman per year)
custom_fertility = [0.05, 0.15, 0.20, 0.18, 0.12, 0.05, 0.01]

engine = SimulationEngine(
    zones=zones,
    mortality_table=custom_mortality,
    fertility_table=custom_fertility
)
```

### Household Formation Parameters

Edit in `demographic_engine.py` in the `DemographicTables` class:
```python
HOUSEHOLD_FORMATION_AGE = 25      # Citizens age >= 25 can form households
HOUSEHOLD_FORMATION_PROB = 0.05   # 5% probability per month
```

## Output & Statistics

### Getting Statistics

```python
# Current population
stats = engine.get_population_stats()
stats['total_population']           # Total living citizens
stats['num_households']             # Number of households
stats['average_household_size']     # Average HH size
stats['num_living_males']          # Total males
stats['num_living_females']        # Total females

# Yearly data (collected after each year)
for year in sorted(engine.yearly_stats.keys()):
    year_data = engine.yearly_stats[year]
    year_data['total_population']           # Population
    year_data['num_households']             # Households
    year_data['average_household_size']    # Avg HH size
    year_data['age_pyramid']                # Age structure
    year_data['num_households_with_children']  # HH with kids
```

### Age Pyramid Data

```python
pyramid = engine.yearly_stats[year]['age_pyramid']

# Males by age group
males_0_5 = pyramid['male']['0-4']

# Females by age group  
females_20_25 = pyramid['female']['20-24']

# All age groups: 0-4, 5-9, 10-14, ..., 80-84, 85+
```

## Visualization

### Population Trends
```python
engine.plot_population_over_time()      # Total population over time
engine.plot_households_over_time()      # Households & avg size
engine.plot_age_pyramid(year=10)        # Age pyramid for year 10
```

## Project Structure

```
urban_abm/
├── demographic_engine.py      # Core engine (main file)
├── example_simulation.py       # Basic example with visualizations
├── test_simulation.py          # Test without visualizations
├── advanced_examples.py        # Advanced usage patterns
├── requirements.txt            # Python dependencies
├── README.md                   # Full documentation
└── QUICKSTART.md              # This file
```

## Troubleshooting

### ModuleNotFoundError: numpy/matplotlib
```bash
pip3 install numpy matplotlib
```

### "python: command not found"
Use `python3` instead of `python`:
```bash
python3 example_simulation.py
```

### Plot windows not appearing
The visualization requires a display. On remote systems, save plots instead:
```python
import matplotlib.pyplot as plt
engine.plot_population_over_time()
plt.savefig('population.png')
```

## Next Steps

1. **Explore the code**: Read `demographic_engine.py` to understand the architecture
2. **Run tests**: Execute `test_simulation.py` to see realistic output
3. **Modify parameters**: Experiment with custom mortality/fertility tables
4. **Build extensions**: Add health, economic, or spatial modules
5. **Integrate data**: Load real demographic data for your region

## Support

For detailed API documentation, see [README.md](README.md).

For code examples, see [advanced_examples.py](advanced_examples.py).
