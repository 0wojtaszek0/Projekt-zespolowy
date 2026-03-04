"""
Module for disease modeling in the simulation.
Handles disease selection, disability weights, and disease initialization.
"""

from typing import Dict, List, Optional


class DiseaseModel:
    """
    Manages disease definitions and characteristics in the simulation.
    
    Attributes:
        diseases: List of selected disease names
        disability_weights: Dictionary mapping disease names to disability weights
        disease_prevalence: Dictionary mapping disease names to prevalence rates
    """
    
    # Top diseases extracted from epidemiological data
    # Note: project now focuses on only two or three conditions.
    # Here we include three most prevalent disorders for simplicity.
    DEFAULT_DISEASES = [
        "Obesity",
        "Hypercholesterolemia",
        "Osteoarthritis",
    ]
    
    # Prevalence rates (%) for the selected diseases
    DEFAULT_PREVALENCE = {
        "Obesity": 44.0,
        "Hypercholesterolemia": 33.1,
        "Osteoarthritis": 30.5,
    }
    
    # Disability weights for each selected disease (0-1 scale)
    # Higher weight = more severe disability
    DEFAULT_DISABILITY_WEIGHTS = {
        "Obesity": 0.15,
        "Hypercholesterolemia": 0.05,
        "Osteoarthritis": 0.20,
    }
    
    # Risk factors and their impact on the (now limited) disease set
    DEFAULT_RISK_FACTORS = {
        "Smoking": {"Hypercholesterolemia": 0.2},
        "Physical inactivity": {"Obesity": 0.3, "Osteoarthritis": 0.25},
        "High-fat diet": {"Obesity": 0.4, "Hypercholesterolemia": 0.2},
    }

    def __init__(
        self,
        diseases: Optional[List[str]] = None,
        disability_weights: Optional[Dict[str, float]] = None,
        prevalence_rates: Optional[Dict[str, float]] = None,
        risk_factors: Optional[Dict[str, Dict[str, float]]] = None,
    ) -> None:
        """
        Initialize the disease model.
        
        Args:
            diseases: List of disease names (defaults to top 15)
            disability_weights: Dictionary mapping disease names to disability scores
            prevalence_rates: Dictionary mapping disease names to prevalence percentages
            risk_factors: Dictionary mapping risk factors to their impact on diseases
        """
        # if user supplied a specific disease list, prune other dictionaries
        self.diseases: List[str] = diseases or self.DEFAULT_DISEASES.copy()
        # filter associated maps to avoid mismatches
        self.disability_weights: Dict[str, float] = (
            {k: v for k, v in (disability_weights or self.DEFAULT_DISABILITY_WEIGHTS).items() if k in self.diseases}
        )
        self.disease_prevalence: Dict[str, float] = (
            {k: v for k, v in (prevalence_rates or self.DEFAULT_PREVALENCE).items() if k in self.diseases}
        )
        self.risk_factors: Dict[str, Dict[str, float]] = (
            {rf: {d: imp for d, imp in diseases.items() if d in self.diseases}
             for rf, diseases in (risk_factors or self.DEFAULT_RISK_FACTORS).items()}
        )

    def get_initial_diseases(self) -> Dict[str, int]:
        """
        Get a dictionary of all diseases initialized to 0 (not present).
        
        Returns:
            Dictionary with disease names as keys and 0 as values
        """
        return {disease: 0 for disease in self.diseases}
    
    def get_prevalence(self, disease_name: str) -> float:
        """
        Get the prevalence rate for a disease.
        
        Args:
            disease_name: Name of the disease
        
        Returns:
            Prevalence rate as percentage (0-100)
        """
        return self.disease_prevalence.get(disease_name, 0.0)
    
    def get_disability_weight(self, disease_name: str) -> float:
        """
        Get the disability weight for a disease.
        
        Args:
            disease_name: Name of the disease
        
        Returns:
            Disability weight (0-1 scale)
        """
        return self.disability_weights.get(disease_name, 0.1)
    
    def get_disease_count(self) -> int:
        """Get the total number of diseases in the model."""
        return len(self.diseases)
    
    def get_all_disability_weights(self) -> Dict[str, float]:
        """Get all disability weights as a dictionary."""
        return self.disability_weights.copy()
    
    def get_risk_factors(self) -> Dict[str, Dict[str, float]]:
        """
        Get the risk factors and their impact on diseases.
        
        Returns:
            Dictionary mapping risk factors to their impact on diseases
        """
        return self.risk_factors.copy()

    def calculate_risk_impact(self, risk_factor: str, disease: str) -> float:
        """
        Calculate the impact of a risk factor on a specific disease.
        
        Args:
            risk_factor: Name of the risk factor
            disease: Name of the disease
        
        Returns:
            Impact value (0-1 scale) or 0 if no impact is defined
        """
        return self.risk_factors.get(risk_factor, {}).get(disease, 0.0)
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"DiseaseModel(diseases={self.get_disease_count()}, total_prevalence={sum(self.disease_prevalence.values()):.1f}%)"
