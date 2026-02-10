"""
URBAN-ABM: Urban Agent-Based Model - Demographic Population Engine

Object-oriented implementation of a demographic simulation with:
- Citizen, Household, and Zone entities
- Age- and sex-dependent mortality
- Fertility-based population growth
- Household formation dynamics
- Statistical tracking and visualization
"""

import random
import numpy as np
from typing import List, Dict, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import matplotlib.pyplot as plt


# ==============================================================================
# DEMOGRAPHIC TABLES (Default realistic values)
# ==============================================================================

class DemographicTables:
    """
    Default demographic parameters for mortality and fertility.
    These are placeholder realistic values and can be overridden.
    """
    
    # Mortality rates by age and sex (per 1000 persons per year)
    # Age groups: [0-1, 1-5, 5-10, 10-15, 15-20, 20-25, 25-30, 30-35, 35-40, 
    #             40-45, 45-50, 50-55, 55-60, 60-65, 65-70, 70-75, 75-80, 80+]
    MORTALITY_TABLE = {
        "M": [6.5, 0.8, 0.4, 0.4, 1.2, 1.5, 1.8, 2.1, 2.6, 
              3.5, 5.0, 7.5, 12.0, 18.0, 27.0, 40.0, 60.0, 100.0],
        "F": [5.5, 0.7, 0.3, 0.3, 0.7, 0.8, 1.0, 1.2, 1.5, 
              2.0, 3.0, 4.5, 7.0, 11.0, 17.0, 28.0, 45.0, 90.0]
    }
    
    # Fertility rates by age (births per woman per year, ages 15-49)
    # Age groups: [15-20, 20-25, 25-30, 30-35, 35-40, 40-45, 45-50]
    FERTILITY_TABLE = [0.05, 0.15, 0.20, 0.18, 0.12, 0.05, 0.01]
    
    # Fertility age range
    FERTILITY_MIN_AGE = 15
    FERTILITY_MAX_AGE = 50
    
    # Household formation threshold
    HOUSEHOLD_FORMATION_AGE = 25
    HOUSEHOLD_FORMATION_PROB = 0.05  # per month
    
    @staticmethod
    def get_mortality_rate(age_years: int, sex: str) -> float:
        """
        Get annual mortality rate for given age and sex.
        
        Args:
            age_years: Age in years
            sex: "M" or "F"
            
        Returns:
            Mortality rate (0-1, as annual probability)
        """
        if sex not in ["M", "F"]:
            raise ValueError("Sex must be 'M' or 'F'")
        
        # Age group mapping
        age_groups = [0, 1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80]
        
        if age_years >= 80:
            idx = -1
        else:
            idx = sum(1 for threshold in age_groups if age_years >= threshold) - 1
        
        rate_per_1000 = DemographicTables.MORTALITY_TABLE[sex][idx]
        return rate_per_1000 / 1000.0
    
    @staticmethod
    def get_fertility_rate(age_years: int) -> float:
        """
        Get annual fertility rate for females of given age.
        
        Args:
            age_years: Age in years
            
        Returns:
            Fertility rate (births per woman per year)
        """
        if age_years < DemographicTables.FERTILITY_MIN_AGE or age_years >= DemographicTables.FERTILITY_MAX_AGE:
            return 0.0
        
        # Map age to fertility table index
        age_offset = age_years - DemographicTables.FERTILITY_MIN_AGE
        idx = min(age_offset // 5, len(DemographicTables.FERTILITY_TABLE) - 1)
        
        return DemographicTables.FERTILITY_TABLE[idx]


# ==============================================================================
# CORE ENTITY CLASSES
# ==============================================================================

@dataclass
class Citizen:
    """
    Represents an individual citizen in the simulation.
    """
    id: int
    sex: str  # "M" or "F"
    age_months: int
    alive: bool = True
    household_id: int = None
    zone_id: int = None
    
    def __post_init__(self):
        if self.sex not in ["M", "F"]:
            raise ValueError("Sex must be 'M' or 'F'")
        if self.age_months < 0:
            raise ValueError("Age in months cannot be negative")
    
    @property
    def age_years(self) -> float:
        """Compute age in years from age_months."""
        return self.age_months / 12.0
    
    def age_one_month(self):
        """Age citizen by one month."""
        if self.alive:
            self.age_months += 1
    
    def is_female(self) -> bool:
        return self.sex == "F"
    
    def can_reproduce(self) -> bool:
        """Check if citizen can reproduce (female, age 15-50)."""
        if not self.is_female():
            return False
        return (DemographicTables.FERTILITY_MIN_AGE <= self.age_years < DemographicTables.FERTILITY_MAX_AGE)
    
    def can_form_household(self) -> bool:
        """Check if citizen can form new household (age >= 25)."""
        return self.age_years >= DemographicTables.HOUSEHOLD_FORMATION_AGE


@dataclass
class Household:
    """
    Represents a household containing citizens.
    """
    id: int
    zone_id: int
    members: List[Citizen] = field(default_factory=list)
    
    def add_member(self, citizen: Citizen):
        """Add citizen to household."""
        if citizen not in self.members:
            self.members.append(citizen)
            citizen.household_id = self.id
    
    def remove_member(self, citizen: Citizen):
        """Remove citizen from household."""
        if citizen in self.members:
            self.members.remove(citizen)
    
    def get_living_members(self) -> List[Citizen]:
        """Get all living citizens in household."""
        return [m for m in self.members if m.alive]
    
    def get_female_members(self) -> List[Citizen]:
        """Get all living females in household."""
        return [m for m in self.get_living_members() if m.is_female()]
    
    def get_size(self) -> int:
        """Get size of household (living members only)."""
        return len(self.get_living_members())


@dataclass
class Zone:
    """
    Represents a spatial district/zone in the simulation.
    """
    id: int
    environmental_params: Dict = field(default_factory=dict)
    
    def set_param(self, key: str, value):
        """Set environmental parameter."""
        self.environmental_params[key] = value
    
    def get_param(self, key: str):
        """Get environmental parameter."""
        return self.environmental_params.get(key)


# ==============================================================================
# SIMULATION ENGINE
# ==============================================================================

class SimulationEngine:
    """
    Main simulation engine managing the demographic ABM.
    """
    
    def __init__(self, zones: List[Zone], mortality_table: Dict = None, 
                 fertility_table: List = None):
        """
        Initialize simulation engine.
        
        Args:
            zones: List of Zone objects
            mortality_table: Dict with "M" and "F" keys containing mortality rates
            fertility_table: List of fertility rates by age
        """
        self.zones = {zone.id: zone for zone in zones}
        self.citizens = {}
        self.households = {}
        self.citizen_id_counter = 0
        self.household_id_counter = 0
        self.current_month = 0
        
        # Override demographic tables if provided
        if mortality_table:
            DemographicTables.MORTALITY_TABLE = mortality_table
        if fertility_table:
            DemographicTables.FERTILITY_TABLE = fertility_table
        
        # Statistics tracking
        self.yearly_stats = defaultdict(dict)
    
    def add_citizen(self, sex: str, age_months: int, zone_id: int, 
                   household_id: int = None) -> Citizen:
        """
        Create and add a new citizen to the simulation.
        
        Args:
            sex: "M" or "F"
            age_months: Age in months
            zone_id: Zone the citizen belongs to
            household_id: Household the citizen belongs to
            
        Returns:
            Created Citizen object
        """
        citizen = Citizen(
            id=self.citizen_id_counter,
            sex=sex,
            age_months=age_months,
            zone_id=zone_id,
            household_id=household_id
        )
        self.citizen_id_counter += 1
        self.citizens[citizen.id] = citizen
        
        # Add to household if specified
        if household_id is not None and household_id in self.households:
            self.households[household_id].add_member(citizen)
        
        return citizen
    
    def create_household(self, zone_id: int) -> Household:
        """
        Create a new household.
        
        Args:
            zone_id: Zone the household is in
            
        Returns:
            Created Household object
        """
        household = Household(id=self.household_id_counter, zone_id=zone_id)
        self.household_id_counter += 1
        self.households[household.id] = household
        return household
    
    def _process_aging(self):
        """Process aging: all living citizens age by 1 month."""
        for citizen in self.citizens.values():
            if citizen.alive:
                citizen.age_one_month()
    
    def _process_mortality(self):
        """
        Process mortality: kill citizens probabilistically based on age/sex.
        """
        for citizen in self.citizens.values():
            if not citizen.alive:
                continue
            
            # Get annual mortality rate
            annual_rate = DemographicTables.get_mortality_rate(
                int(citizen.age_years), citizen.sex
            )
            
            # Convert to monthly probability
            monthly_prob = 1.0 - (1.0 - annual_rate) ** (1.0 / 12.0)
            
            # Kill probabilistically
            if random.random() < monthly_prob:
                citizen.alive = False
    
    def _process_fertility(self):
        """
        Process fertility: create newborns for reproductive-age females.
        """
        newborns = []
        
        # Create a list snapshot to avoid dictionary changes during iteration
        citizens_snapshot = list(self.citizens.values())
        
        for citizen in citizens_snapshot:
            if not citizen.alive or not citizen.can_reproduce():
                continue
            
            # Get annual fertility rate
            annual_rate = DemographicTables.get_fertility_rate(int(citizen.age_years))
            
            # Convert to monthly probability
            monthly_prob = annual_rate / 12.0
            
            # Create newborn probabilistically
            if random.random() < monthly_prob:
                newborn = self.add_citizen(
                    sex=random.choice(["M", "F"]),
                    age_months=0,
                    zone_id=citizen.zone_id,
                    household_id=citizen.household_id
                )
                newborns.append(newborn)
        
        return newborns
    
    def _process_household_formation(self):
        """
        Process household formation: eligible citizens may form new households.
        """
        for citizen in list(self.citizens.values()):
            if not citizen.alive or not citizen.can_form_household():
                continue
            
            # Skip if already forming (newly created household)
            if citizen.household_id is None:
                continue
            
            # Probabilistically form household
            if random.random() < DemographicTables.HOUSEHOLD_FORMATION_PROB:
                old_household = self.households[citizen.household_id]
                new_household = self.create_household(citizen.zone_id)
                
                old_household.remove_member(citizen)
                new_household.add_member(citizen)
    
    def step(self):
        """
        Execute one simulation step (1 month).
        """
        self._process_aging()
        self._process_mortality()
        self._process_fertility()
        self._process_household_formation()
        
        self.current_month += 1
    
    def run(self, months: int):
        """
        Run simulation for specified number of months.
        
        Args:
            months: Number of months to simulate
        """
        for _ in range(months):
            self.step()
            
            # Collect statistics at end of each year
            if self.current_month % 12 == 0:
                self.collect_yearly_stats()
    
    def collect_yearly_stats(self):
        """Collect statistics at the end of each year."""
        year = self.current_month // 12
        
        # Total population
        living_citizens = [c for c in self.citizens.values() if c.alive]
        total_pop = len(living_citizens)
        
        # Age pyramid
        age_pyramid = self._compute_age_pyramid(living_citizens)
        
        # Number of households
        num_households = len([h for h in self.households.values() 
                             if h.get_size() > 0])
        
        self.yearly_stats[year] = {
            'total_population': total_pop,
            'age_pyramid': age_pyramid,
            'num_households': num_households,
            'num_households_with_children': self._count_households_with_children(),
            'average_household_size': (total_pop / num_households if num_households > 0 else 0)
        }
    
    def _compute_age_pyramid(self, citizens: List[Citizen]) -> Dict:
        """
        Compute age pyramid in 5-year bins separated by sex.
        
        Args:
            citizens: List of citizens to analyze
            
        Returns:
            Dict with age groups and counts
        """
        pyramid = {
            'male': defaultdict(int),
            'female': defaultdict(int)
        }
        
        age_bins = [(i, i+5) for i in range(0, 85, 5)]
        age_bins.append((85, 150))
        
        for citizen in citizens:
            age_y = int(citizen.age_years)
            
            for bin_start, bin_end in age_bins:
                if bin_start <= age_y < bin_end:
                    bin_label = f"{bin_start}-{bin_end-1}"
                    if citizen.is_female():
                        pyramid['female'][bin_label] += 1
                    else:
                        pyramid['male'][bin_label] += 1
                    break
        
        return dict(pyramid)
    
    def _count_households_with_children(self) -> int:
        """Count households with children (age < 18)."""
        count = 0
        for household in self.households.values():
            for member in household.get_living_members():
                if member.age_years < 18:
                    count += 1
                    break
        return count
    
    def get_population_stats(self) -> Dict:
        """Get current population statistics."""
        living_citizens = [c for c in self.citizens.values() if c.alive]
        
        return {
            'total_population': len(living_citizens),
            'num_households': len([h for h in self.households.values() if h.get_size() > 0]),
            'average_household_size': (len(living_citizens) / len([h for h in self.households.values() if h.get_size() > 0]) 
                                      if len([h for h in self.households.values() if h.get_size() > 0]) > 0 else 0),
            'num_living_males': len([c for c in living_citizens if not c.is_female()]),
            'num_living_females': len([c for c in living_citizens if c.is_female()]),
        }
    
    # ==============================================================================
    # PLOTTING AND VISUALIZATION
    # ==============================================================================
    
    def plot_age_pyramid(self, year: int = None):
        """
        Plot population age pyramid for a specific year.
        
        Args:
            year: Year to plot (if None, uses latest year)
        """
        if year is None:
            year = max(self.yearly_stats.keys()) if self.yearly_stats else 0
        
        if year not in self.yearly_stats:
            print(f"No statistics available for year {year}")
            return
        
        pyramid = self.yearly_stats[year]['age_pyramid']
        age_bins = [f"{i}-{i+4}" for i in range(0, 85, 5)] + ["85+"]
        
        male_counts = [pyramid['male'].get(bin_label, 0) for bin_label in age_bins]
        female_counts = [pyramid['female'].get(bin_label, 0) for bin_label in age_bins]
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        y_pos = np.arange(len(age_bins))
        ax.barh(y_pos, [-x for x in male_counts], label='Male', color='steelblue')
        ax.barh(y_pos, female_counts, label='Female', color='coral')
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(age_bins)
        ax.set_xlabel('Population Count')
        ax.set_ylabel('Age Group')
        ax.set_title(f'Population Age Pyramid - Year {year}')
        ax.legend()
        ax.axvline(x=0, color='black', linewidth=0.8)
        
        plt.tight_layout()
        plt.show()
    
    def plot_population_over_time(self):
        """Plot total population over simulation time."""
        if not self.yearly_stats:
            print("No statistics collected yet")
            return
        
        years = sorted(self.yearly_stats.keys())
        populations = [self.yearly_stats[year]['total_population'] for year in years]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(years, populations, marker='o', linewidth=2, markersize=6, color='darkblue')
        ax.set_xlabel('Year')
        ax.set_ylabel('Population')
        ax.set_title('Total Population Over Time')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def plot_households_over_time(self):
        """Plot number of households over simulation time."""
        if not self.yearly_stats:
            print("No statistics collected yet")
            return
        
        years = sorted(self.yearly_stats.keys())
        num_households = [self.yearly_stats[year]['num_households'] for year in years]
        avg_size = [self.yearly_stats[year]['average_household_size'] for year in years]
        
        fig, ax1 = plt.subplots(figsize=(10, 6))
        
        # Primary axis: number of households
        color = 'darkgreen'
        ax1.set_xlabel('Year')
        ax1.set_ylabel('Number of Households', color=color)
        ax1.plot(years, num_households, marker='s', linewidth=2, markersize=6, 
                color=color, label='Number of Households')
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.grid(True, alpha=0.3)
        
        # Secondary axis: average household size
        ax2 = ax1.twinx()
        color = 'darkred'
        ax2.set_ylabel('Average Household Size', color=color)
        ax2.plot(years, avg_size, marker='^', linewidth=2, markersize=6, 
                color=color, label='Avg Household Size', linestyle='--')
        ax2.tick_params(axis='y', labelcolor=color)
        
        fig.suptitle('Household Statistics Over Time')
        fig.tight_layout()
        plt.show()


# ==============================================================================
# INITIALIZATION HELPERS
# ==============================================================================

def create_initial_population(engine: SimulationEngine, zone_ids: List[int], 
                             initial_population: int, 
                             age_distribution: str = "uniform"):
    """
    Create an initial population with reasonable demographic structure.
    
    Args:
        engine: SimulationEngine instance
        zone_ids: List of zone IDs to populate
        initial_population: Target population size
        age_distribution: "uniform" or "realistic"
    """
    people_per_zone = initial_population // len(zone_ids)
    household_size = 3  # Average household size
    
    for zone_id in zone_ids:
        households_needed = max(1, people_per_zone // household_size)
        
        for _ in range(households_needed):
            household = engine.create_household(zone_id)
            
            # Create household members with age distribution
            num_members = random.randint(1, 5)
            for _ in range(num_members):
                if age_distribution == "realistic":
                    # Skew towards younger population
                    age_years = abs(np.random.normal(35, 25))
                    age_years = min(100, max(0, age_years))
                else:
                    age_years = random.uniform(0, 80)
                
                sex = random.choice(["M", "F"])
                citizen = engine.add_citizen(
                    sex=sex,
                    age_months=int(age_years * 12),
                    zone_id=zone_id,
                    household_id=household.id
                )
