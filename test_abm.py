"""
Unit tests for the Urban Health ABM simulation modules.
Tests core functionality of Citizen, Household, DiseaseModel, and SimulationEngine.
"""

import unittest
from citizen import Citizen
from household import Household
from disease_model import DiseaseModel
from simulation_engine import SimulationEngine


class TestCitizen(unittest.TestCase):
    """Test cases for the Citizen class."""
    
    def setUp(self):
        """Create test citizen before each test."""
        self.disease_dict = {"Obesity": 0, "Hypertension": 1}
        self.citizen = Citizen(
            sex="female",
            age_months=25*12,  # 25 years
            household_id=1,
            diseases=self.disease_dict,
        )
    
    def test_citizen_creation(self):
        """Test basic citizen creation."""
        self.assertTrue(self.citizen.alive)
        self.assertEqual(self.citizen.age_years, 25.0)
        self.assertEqual(self.citizen.sex, "female")
    
    def test_age_one_month(self):
        """Test aging by one month."""
        initial_age = self.citizen.age_months
        self.citizen.age_one_month()
        self.assertEqual(self.citizen.age_months, initial_age + 1)
    
    def test_num_conditions(self):
        """Test counting diseases."""
        count = self.citizen.num_conditions()
        self.assertEqual(count, 1)  # Only Hypertension
    
    def test_multimorbidity(self):
        """Test multimorbidity detection."""
        self.assertFalse(self.citizen.has_multimorbidity())
        self.citizen.diseases["Obesity"] = 1
        self.assertTrue(self.citizen.has_multimorbidity())
    
    def test_disability_score(self):
        """Test disability score computation."""
        self.citizen.compute_disability_score()
        self.assertGreater(self.citizen.disability_score, 0)
    
    def test_mortality_risk_age(self):
        """Test that mortality risk increases with age."""
        young = Citizen("male", 25*12, 1)
        old = Citizen("male", 75*12, 1)
        
        young_risk = young.mortality_risk()
        old_risk = old.mortality_risk()
        
        self.assertLess(young_risk, old_risk)
    
    def test_fertility_probability_female(self):
        """Test fertility for fertile female."""
        fertile_female = Citizen("female", 27*12, 1)  # 27 years
        prob = fertile_female.fertility_probability()
        self.assertGreater(prob, 0)
    
    def test_fertility_probability_male(self):
        """Test that males have zero fertility."""
        male = Citizen("male", 27*12, 1)
        prob = male.fertility_probability()
        self.assertEqual(prob, 0)
    
    def test_female_mortality_advantage(self):
        """Test that females have lower mortality."""
        male = Citizen("male", 50*12, 1)
        female = Citizen("female", 50*12, 1)
        
        male_risk = male.mortality_risk()
        female_risk = female.mortality_risk()
        
        self.assertLess(female_risk, male_risk)


class TestHousehold(unittest.TestCase):
    """Test cases for the Household class."""
    
    def setUp(self):
        """Create test household before each test."""
        self.household = Household(zone_id=1)
    
    def test_household_creation(self):
        """Test basic household creation."""
        self.assertEqual(self.household.size(), 0)
        self.assertTrue(self.household.is_empty())
    
    def test_add_member(self):
        """Test adding members."""
        self.household.add_member(1)
        self.assertEqual(self.household.size(), 1)
        self.assertFalse(self.household.is_empty())
    
    def test_remove_member(self):
        """Test removing members."""
        self.household.add_member(1)
        self.household.add_member(2)
        self.household.remove_member(1)
        self.assertEqual(self.household.size(), 1)
    
    def test_duplicate_member(self):
        """Test that same member isn't added twice."""
        self.household.add_member(1)
        self.household.add_member(1)
        self.assertEqual(self.household.size(), 1)


class TestDiseaseModel(unittest.TestCase):
    """Test cases for the DiseaseModel class."""
    
    def setUp(self):
        """Create test disease model before each test."""
        self.model = DiseaseModel()
    
    def test_default_diseases(self):
        """Test that default diseases are set."""
        self.assertEqual(self.model.get_disease_count(), 15)
    
    def test_initial_diseases_dict(self):
        """Test that initial diseases dict is all zeros."""
        diseases = self.model.get_initial_diseases()
        self.assertEqual(len(diseases), 15)
        for disease, value in diseases.items():
            self.assertEqual(value, 0)
    
    def test_prevalence_retrieval(self):
        """Test getting disease prevalence."""
        prevalence = self.model.get_prevalence("Obesity")
        self.assertEqual(prevalence, 44.0)
    
    def test_disability_weight_retrieval(self):
        """Test getting disability weight."""
        weight = self.model.get_disability_weight("Osteoarthritis")
        self.assertEqual(weight, 0.20)


class TestSimulationEngine(unittest.TestCase):
    """Test cases for the SimulationEngine class."""
    
    def setUp(self):
        """Create test engine before each test."""
        self.engine = SimulationEngine(seed=42)
    
    def test_engine_creation(self):
        """Test basic engine creation."""
        self.assertEqual(len(self.engine.citizens), 0)
        self.assertEqual(len(self.engine.households), 0)
        self.assertEqual(self.engine.current_month, 0)
    
    def test_synthetic_population_creation(self):
        """Test creating synthetic population."""
        count = self.engine._create_synthetic_population(100)
        self.assertEqual(count, 100)
        self.assertEqual(len(self.engine.citizens), 100)
        self.assertGreater(len(self.engine.households), 0)
    
    def test_step_increments_month(self):
        """Test that step increments current month."""
        self.engine._create_synthetic_population(10)
        initial_month = self.engine.current_month
        self.engine.step()
        self.assertEqual(self.engine.current_month, initial_month + 1)
    
    def test_yearly_stats_collection(self):
        """Test that yearly stats are collected."""
        self.engine._create_synthetic_population(50)
        self.engine.collect_yearly_stats(year=1)
        
        self.assertIn(1, self.engine.yearly_stats)
        stats = self.engine.yearly_stats[1]
        self.assertIn("total_population", stats)
        self.assertIn("num_households", stats)
        self.assertIn("average_household_size", stats)
    
    def test_short_simulation(self):
        """Test running a short simulation (12 months = 1 year)."""
        self.engine._create_synthetic_population(50)
        initial_pop = len(self.engine.citizens)
        
        self.engine.run(months=12)  # Run for 1 year to collect stats
        
        # Population may increase or decrease, but should have statistics
        self.assertGreater(len(self.engine.yearly_stats), 0)


class TestIntegration(unittest.TestCase):
    """Integration tests combining multiple components."""
    
    def test_full_simulation_workflow(self):
        """Test complete simulation workflow."""
        # Create and initialize engine
        engine = SimulationEngine(seed=42)
        engine.fertility_rate = 1.0
        engine.mortality_multiplier = 1.0
        
        # Create population
        count = engine._create_synthetic_population(100)
        self.assertEqual(count, 100)
        
        # Run simulation
        engine.run(months=12)
        
        # Check results
        self.assertIn(1, engine.yearly_stats)
        stats = engine.yearly_stats[1]
        self.assertGreater(stats["total_population"], 0)
        self.assertGreater(stats["num_households"], 0)


if __name__ == "__main__":
    # Run all tests with verbose output
    unittest.main(verbosity=2)
