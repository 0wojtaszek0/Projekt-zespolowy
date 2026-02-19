"""
Main simulation engine for the Agent-Based Model.
Orchestrates the simulation loop and handles all demographic events.
"""

from typing import Dict, List, Tuple
import random
import pandas as pd

from citizen import Citizen
from household import Household
from disease_model import DiseaseModel


class SimulationEngine:
    """
    Main simulation engine managing population dynamics.
    
    Attributes:
        citizens: Dictionary mapping citizen IDs to Citizen objects
        households: Dictionary mapping household IDs to Household objects
        disease_model: DiseaseModel instance
        current_month: Current month in simulation
        yearly_stats: Dictionary storing statistics for each year
        rng: Random number generator for reproducibility
    """
    
    def __init__(
        self,
        disease_model: DiseaseModel | None = None,
        seed: int | None = None,
    ) -> None:
        """
        Initialize the simulation engine.
        
        Args:
            disease_model: DiseaseModel instance (creates default if None)
            seed: Random seed for reproducibility
        """
        self.disease_model: DiseaseModel = disease_model or DiseaseModel()
        self.citizens: Dict[int, Citizen] = {}
        self.households: Dict[int, Household] = {}
        self.current_month: int = 0
        self.yearly_stats: Dict[int, Dict] = {}
        self.rng: random.Random = random.Random(seed)
        self.fertility_rate: float = 1.0
        self.mortality_multiplier: float = 1.0
        self.household_split_probability: float = 0.001
    
    def load_initial_population(
        self,
        filepath: str = "population_data.xlsx",
        min_age: int = 20,
        max_age: int = 80,
    ) -> int:
        """
        Load initial population from Excel file or create synthetic if not found.
        
        The Excel file should have columns:
        - id, sex, age (in years), household_id, zone_id
        - Plus columns for diseases (0/1)
        
        Args:
            filepath: Path to Excel file (optional)
            min_age: Minimum age to include (years)
            max_age: Maximum age to include (years)
        
        Returns:
            Number of citizens loaded
        """
        try:
            df = pd.read_excel(filepath)
            print(f"Loaded from {filepath}: {len(df)} potential citizens")
        except Exception as e:
            print(f"Could not load from Excel ({e}). Creating synthetic population.")
            return self._create_synthetic_population(1600)
        
        # Assume Excel has columns: id, sex, age, household_id, zone_id, and disease columns
        diseases_list = self.disease_model.diseases
        
        count = 0
        households_seen = set()
        
        for _, row in df.iterrows():
            # Skip invalid ages
            if pd.isna(row.get("age")):
                continue
            
            age = int(row["age"])
            if age < min_age or age > max_age:
                continue
            
            sex = str(row.get("sex", "")).lower()
            if sex not in ["male", "female", "m", "f"]:
                sex = self.rng.choice(["male", "female"])
            
            # Normalize sex
            if sex == "m":
                sex = "male"
            elif sex == "f":
                sex = "female"
            
            # Create citizen
            age_months = age * 12 + self.rng.randint(0, 11)
            
            # Get diseases
            diseases_dict = self.disease_model.get_initial_diseases()
            for disease in diseases_list:
                if disease in row and row[disease] == 1:
                    diseases_dict[disease] = 1
            
            household_id = int(row.get("household_id", 0)) or self.rng.randint(1, 1000)
            zone_id = int(row.get("zone_id", 0)) or 1
            
            citizen = Citizen(
                sex=sex,
                age_months=age_months,
                household_id=household_id,
                diseases=diseases_dict,
            )
            
            citizen.compute_disability_score(
                self.disease_model.get_all_disability_weights()
            )
            
            self.citizens[citizen.id] = citizen
            count += 1
        
        # Create households for all citizens
        for citizen in self.citizens.values():
            if citizen.household_id not in self.households:
                zone_id = self.rng.randint(1, 4)
                household = Household(zone_id)
                self.households[household.id] = household
                citizen.household_id = household.id
            self.households[citizen.household_id].add_member(citizen.id)
        
        return count
    
    def _create_synthetic_population(self, size: int = 1600) -> int:
        """
        Create a synthetic population for testing.
        
        Args:
            size: Number of citizens to create
        
        Returns:
            Number of citizens created
        """
        print(f"Creating synthetic population of {size} citizens...")
        
        for zone_id in range(1, 4):
            household = Household(zone_id)
            self.households[household.id] = household
        
        for _ in range(size):
            sex = self.rng.choice(["male", "female"])
            age = self.rng.randint(20, 80)
            age_months = age * 12 + self.rng.randint(0, 11)
            
            diseases_dict = self.disease_model.get_initial_diseases()
            for disease in self.disease_model.diseases:
                prevalence = self.disease_model.get_prevalence(disease) / 100.0
                if self.rng.random() < prevalence:
                    diseases_dict[disease] = 1
            
            household_id = self.rng.choice(list(self.households.keys()))
            
            citizen = Citizen(
                sex=sex,
                age_months=age_months,
                household_id=household_id,
                diseases=diseases_dict,
            )
            citizen.compute_disability_score(
                self.disease_model.get_all_disability_weights()
            )
            
            self.citizens[citizen.id] = citizen
            self.households[household_id].add_member(citizen.id)
        
        return size
    
    def run(self, months: int = 600) -> None:
        """
        Run the simulation for a specified number of months.
        
        Args:
            months: Number of months to simulate
        """
        print(f"Starting simulation for {months} months ({months/12:.1f} years)")
        print(f"Initial population: {len(self.citizens)} citizens")
        
        for month in range(months):
            self.step()
            
            # Collect yearly statistics
            if (month + 1) % 12 == 0:
                year = (month + 1) // 12
                self.collect_yearly_stats(year)
                if year % 5 == 0 or year == 1:
                    print(f"Year {year}: Population={len([c for c in self.citizens.values() if c.alive])}, "
                          f"Households={len(self.households)}")
        
        print(f"Simulation complete. Final population: {len([c for c in self.citizens.values() if c.alive])}")
    
    def step(self) -> None:
        """Execute one month of simulation."""
        self.current_month += 1
        
        # Age all citizens
        for citizen in self.citizens.values():
            if citizen.alive:
                citizen.age_one_month()
        
        # Handle deaths
        self.handle_deaths()
        
        # Handle births
        self.handle_births()
        
        # Handle household splits
        self.handle_household_splits()
    
    def handle_deaths(self) -> None:
        """Process deaths for all living citizens."""
        deaths = []
        for citizen_id, citizen in self.citizens.items():
            if citizen.alive and citizen.maybe_die(self.rng):
                deaths.append(citizen_id)
        
        # Remove deceased from households
        for citizen_id in deaths:
            citizen = self.citizens[citizen_id]
            household = self.households.get(citizen.household_id)
            if household:
                household.remove_member(citizen_id)
    
    def handle_births(self) -> None:
        """Process births for eligible females."""
        births = []
        
        for citizen in self.citizens.values():
            if (citizen.alive and 
                citizen.sex == "female" and 
                citizen.maybe_give_birth(self.rng)):
                births.append(citizen)
        
        # Create newborns
        for mother in births:
            newborn_sex = self.rng.choice(["male", "female"])
            
            newborn = Citizen(
                sex=newborn_sex,
                age_months=0,
                household_id=mother.household_id,
                diseases=self.disease_model.get_initial_diseases(),
            )
            
            self.citizens[newborn.id] = newborn
            
            household = self.households.get(mother.household_id)
            if household:
                household.add_member(newborn.id)
    
    def handle_household_splits(self) -> None:
        """
        Handle young adults leaving to form new households.
        
        Adults aged 25+ may leave their current household
        with some probability to form new households.
        """
        potential_movers = []
        
        for citizen in self.citizens.values():
            if (citizen.alive and 
                citizen.age_years >= 25 and 
                self.rng.random() < self.household_split_probability):
                potential_movers.append(citizen)
        
        # Move to new households
        for citizen in potential_movers:
            old_household = self.households.get(citizen.household_id)
            if old_household:
                old_household.remove_member(citizen.id)
            
            # Create new household
            zone_id = old_household.zone_id if old_household else 1
            new_household = Household(zone_id)
            self.households[new_household.id] = new_household
            new_household.add_member(citizen.id)
            citizen.household_id = new_household.id
    
    def collect_yearly_stats(self, year: int) -> None:
        """
        Collect population statistics for a given year.
        
        Args:
            year: Year number (1-50)
        """
        alive_citizens = [c for c in self.citizens.values() if c.alive]
        
        if not alive_citizens:
            self.yearly_stats[year] = {
                "total_population": 0,
                "num_households": 0,
                "average_household_size": 0,
                "num_males": 0,
                "num_females": 0,
                "age_pyramid": {},
            }
            return
        
        # Basic stats
        males = [c for c in alive_citizens if c.sex == "male"]
        females = [c for c in alive_citizens if c.sex == "female"]
        
        # Households with members
        active_households = [
            h for h in self.households.values() 
            if h.size() > 0 and any(
                self.citizens[m_id].alive for m_id in h.members 
                if m_id in self.citizens
            )
        ]
        
        avg_household_size = (
            sum(h.size() for h in active_households) / len(active_households)
            if active_households else 0
        )
        
        # Age pyramid (5-year bins)
        age_pyramid = self._build_age_pyramid(alive_citizens)
        
        self.yearly_stats[year] = {
            "total_population": len(alive_citizens),
            "num_households": len(active_households),
            "average_household_size": avg_household_size,
            "num_males": len(males),
            "num_females": len(females),
            "age_pyramid": age_pyramid,
            "multimorbidity_count": sum(
                1 for c in alive_citizens if c.has_multimorbidity()
            ),
            "average_disability_score": (
                sum(c.disability_score for c in alive_citizens) / len(alive_citizens)
            ) if alive_citizens else 0.0,
        }
    
    def _build_age_pyramid(self, citizens: List[Citizen]) -> Dict[str, Dict[str, int]]:
        """
        Build age pyramid data for visualization.
        
        Args:
            citizens: List of citizens to include
        
        Returns:
            Dictionary with age bins and male/female counts
        """
        pyramid = {}
        
        # Create 5-year age bins
        for start_age in range(20, 85, 5):
            end_age = start_age + 5
            bin_name = f"{start_age}-{end_age-1}"
            
            males = sum(
                1 for c in citizens 
                if c.sex == "male" and start_age <= c.age_years < end_age
            )
            females = sum(
                1 for c in citizens 
                if c.sex == "female" and start_age <= c.age_years < end_age
            )
            
            pyramid[bin_name] = {"male": males, "female": females}
        
        return pyramid
    
    def get_statistics_summary(self) -> str:
        """Get a text summary of simulation statistics."""
        lines = ["=" * 70]
        lines.append("SIMULATION STATISTICS")
        lines.append("=" * 70)
        
        if not self.yearly_stats:
            lines.append("No statistics collected yet.")
            return "\n".join(lines)
        
        final_year = max(self.yearly_stats.keys())
        stats = self.yearly_stats[final_year]
        
        lines.append(f"Year: {final_year}")
        lines.append(f"Total Population: {stats['total_population']}")
        total_pop = max(stats['total_population'], 1)
        lines.append(f"Male: {stats['num_males']} ({stats['num_males']/total_pop*100:.1f}%)")
        lines.append(f"Female: {stats['num_females']} ({stats['num_females']/total_pop*100:.1f}%)")
        lines.append(f"Number of Households: {stats['num_households']}")
        lines.append(f"Average Household Size: {stats['average_household_size']:.2f}")
        lines.append(f"Multimorbidity Cases: {stats.get('multimorbidity_count', 0)}")
        lines.append(f"Average Disability Score: {stats.get('average_disability_score', 0.0):.3f}")
        lines.append("=" * 70)
        
        return "\n".join(lines)
