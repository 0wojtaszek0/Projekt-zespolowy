"""
Minimal visualization stub for the Urban Health ABM.

The real project previously generated Plotly HTML files; for the purposes
of automated testing and demonstration we provide a lightweight placeholder
that simply records that methods were called.  This prevents import errors
and allows the simulation to run without heavy plotting dependencies.
"""

from typing import Dict, Any


class SimulationVisualizer:
    def __init__(self, yearly_stats: Dict[int, Any]) -> None:
        self.yearly_stats = yearly_stats

    def plot_interactive_age_pyramid(self) -> None:
        print("[Visualization] would plot interactive age pyramid here")

    def plot_population_trends(self) -> None:
        print("[Visualization] would plot population trends here")

    def plot_households_trends(self) -> None:
        print("[Visualization] would plot household trends here")

    def plot_gender_distribution(self) -> None:
        print("[Visualization] would plot gender distribution here")

    def generate_all_plots(self) -> None:
        # call each plotting method so that any code expecting them sees no error
        self.plot_interactive_age_pyramid()
        self.plot_population_trends()
        self.plot_households_trends()
        self.plot_gender_distribution()
        print("[Visualization] all plots generated (stub)")
