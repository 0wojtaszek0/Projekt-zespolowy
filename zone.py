"""
Simple representation of a geographic zone used by the simulation engine.
The original workspace omitted this file, so it's provided here to make
`simulation_engine` importable and to hold basic environmental parameters.

Attributes:
    id: automatically assigned integer unique identifier
    environmental_parameters: dictionary with keys such as
        - air_quality
        - greenery_index
        - healthcare_access
        - population_density

Methods:
    (none yet, zones are immutable once created)
"""

import itertools
from typing import Dict


class Zone:
    _id_counter = itertools.count(1)

    def __init__(self, parameters: Dict[str, float]) -> None:
        """Initialize a zone with a unique id and given parameters."""
        self.id: int = next(Zone._id_counter)
        # copy to avoid external mutation
        self.environmental_parameters: Dict[str, float] = parameters.copy()

    def __repr__(self) -> str:
        return f"Zone(id={self.id}, params={self.environmental_parameters})"
