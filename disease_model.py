"""
Module for disease modeling in the simulation.
Handles disease selection, disability weights, and disease initialization.
"""

from typing import Dict, List


class DiseaseModel:
    """
    Manages disease definitions and characteristics in the simulation.
    
    Attributes:
        diseases: List of selected disease names
        disability_weights: Dictionary mapping disease names to disability weights
        disease_prevalence: Dictionary mapping disease names to prevalence rates
    """
    
    # Top 15 diseases extracted from epidemiological data
    DEFAULT_DISEASES = [
        "Obesity",
        "Hypercholesterolemia",
        "Osteoarthritis",
        "Hypertension",
        "Allergy",
        "Focal thyroid lesions",
        "Lower limb varicose veins",
        "Rectal varices",
        "Hypertriglyceridemia",
        "Gastroesophageal reflux disease",
        "Peptic ulcer disease",
        "Discopathy",
        "Migraine",
        "Cholelithiasis",
        "Fatty liver disease",
    ]
    
    # Prevalence rates (%) from epidemiological data
    DEFAULT_PREVALENCE = {
        "Obesity": 44.0,
        "Hypercholesterolemia": 33.1,
        "Osteoarthritis": 30.5,
        "Hypertension": 28.5,
        "Allergy": 22.0,
        "Focal thyroid lesions": 18.1,
        "Lower limb varicose veins": 17.7,
        "Rectal varices": 17.7,
        "Hypertriglyceridemia": 17.1,
        "Gastroesophageal reflux disease": 14.8,
        "Peptic ulcer disease": 12.1,
        "Discopathy": 11.7,
        "Migraine": 10.9,
        "Cholelithiasis": 10.1,
        "Fatty liver disease": 9.2,
    }
    
    # Disability weights for each disease (0-1 scale)
    # Higher weight = more severe disability
    DEFAULT_DISABILITY_WEIGHTS = {
        "Obesity": 0.15,
        "Hypercholesterolemia": 0.05,
        "Osteoarthritis": 0.20,
        "Hypertension": 0.10,
        "Allergy": 0.03,
        "Focal thyroid lesions": 0.05,
        "Lower limb varicose veins": 0.12,
        "Rectal varices": 0.12,
        "Hypertriglyceridemia": 0.08,
        "Gastroesophageal reflux disease": 0.10,
        "Peptic ulcer disease": 0.12,
        "Discopathy": 0.18,
        "Migraine": 0.08,
        "Cholelithiasis": 0.10,
        "Fatty liver disease": 0.15,
    }
    
    def __init__(
        self,
        diseases: List[str] | None = None,
        disability_weights: Dict[str, float] | None = None,
        prevalence_rates: Dict[str, float] | None = None,
    ) -> None:
        """
        Initialize the disease model.
        
        Args:
            diseases: List of disease names (defaults to top 15)
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
