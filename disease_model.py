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
    
    # Top 3 diseases selected for the simulation (dependency graph diseases)
    DEFAULT_DISEASES = [
        "Cardiovascular Disease",
        "Type 2 Diabetes",
        "Chronic Respiratory Disease",
    ]

    # Prevalence rates (%) for the selected diseases
    DEFAULT_PREVALENCE = {
        "Cardiovascular Disease": 25.0,
        "Type 2 Diabetes": 10.0,
        "Chronic Respiratory Disease": 15.0,
    }

    # Disability weights for the selected diseases (0-1 scale)
    DEFAULT_DISABILITY_WEIGHTS = {
        "Cardiovascular Disease": 0.25,
        "Type 2 Diabetes": 0.20,
        "Chronic Respiratory Disease": 0.22,
    }
    
    def __init__(
        self,
        diseases: Optional[List[str]] = None,
        disability_weights: Optional[Dict[str, float]] = None,
        prevalence_rates: Optional[Dict[str, float]] = None,
    ) -> None:
        """
        Initialize the disease model.
        
        Args:
            diseases: List of disease names (defaults to top 3)
            disability_weights: Dictionary mapping disease names to disability scores
            prevalence_rates: Dictionary mapping disease names to prevalence percentages
        """
        self.diseases: List[str] = diseases or self.DEFAULT_DISEASES.copy()
        self.disability_weights: Dict[str, float] = (
            disability_weights or self.DEFAULT_DISABILITY_WEIGHTS.copy()
        )
        self.disease_prevalence: Dict[str, float] = (
            prevalence_rates or self.DEFAULT_PREVALENCE.copy()
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
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"DiseaseModel(diseases={self.get_disease_count()}, total_prevalence={sum(self.disease_prevalence.values()):.1f}%)"
