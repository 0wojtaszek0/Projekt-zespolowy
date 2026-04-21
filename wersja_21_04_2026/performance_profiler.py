"""
Performance Profiling & Memory Analysis Tools

Narzędzia do:
- Pomiaru czasu wykonania poszczególnych kroków symulacji
- Analizy zużycia pamięci przez agentów
- Identyfikacji bottlenecków
- Optymalizacji struktury danych
"""

import time
import psutil
import os
import sys
from typing import Dict, Callable, List, Tuple
from functools import wraps
from simulation_engine import SimulationEngine
from disease_model import DiseaseModel
import json
from datetime import datetime


class PerformanceProfiler:
    """Narzędzie do profilowania wydajności symulacji."""
    
    def __init__(self):
        """Inicjalizuj profiler."""
        self.timings: Dict[str, List[float]] = {}
        self.memory_snapshots: Dict[str, Dict] = {}
        self.start_time = None
        self.total_steps = 0
    
    def time_function(self, func_name: str):
        """
        Dekorator do mierzenia czasu wykonania funkcji.
        
        Usage:
            profiler = PerformanceProfiler()
            
            @profiler.time_function("step_execution")
            def do_simulation_step():
                ...
        """
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start = time.perf_counter()
                result = func(*args, **kwargs)
                elapsed = time.perf_counter() - start
                
                if func_name not in self.timings:
                    self.timings[func_name] = []
                self.timings[func_name].append(elapsed)
                
                return result
            return wrapper
        return decorator
    
    def profile_simulation_step(self, engine: SimulationEngine, num_steps: int = 10):
        """
        Wykonaj kilka kroków symulacji i zmierz czas każdego kroku.
        
        Args:
            engine: SimulationEngine instance
            num_steps: Liczba kroków do zmierzenia
        """
        print("\n" + "="*70)
        print("PROFILING SIMULATION STEPS")
        print("="*70)
        
        step_times = []
        
        print(f"\nExecuting {num_steps} simulation steps...\n")
        
        for i in range(num_steps):
            step_start = time.perf_counter()
            
            # Wykonaj jeden krok symulacji
            engine.step()
            
            step_elapsed = time.perf_counter() - step_start
            step_times.append(step_elapsed)
            
            if (i + 1) % 5 == 0 or i == 0:
                avg_time = sum(step_times) / len(step_times)
                print(f"Step {i+1:3d}: {step_elapsed*1000:7.2f}ms | Avg: {avg_time*1000:7.2f}ms")
        
        # Analiza wyników
        print("\n" + "-"*70)
        print("PROFILING RESULTS:")
        print("-"*70)
        print(f"Total steps: {num_steps}")
        print(f"Total time: {sum(step_times):.2f}s")
        print(f"Average step time: {sum(step_times)/len(step_times)*1000:.2f}ms")
        print(f"Min step time: {min(step_times)*1000:.2f}ms")
        print(f"Max step time: {max(step_times)*1000:.2f}ms")
        
        # Sprawdź czy czasy rosną (wskaż bottlenecks)
        if len(step_times) > 1:
            first_half = sum(step_times[:num_steps//2]) / (num_steps//2)
            second_half = sum(step_times[num_steps//2:]) / (num_steps - num_steps//2)
            
            if second_half > first_half * 1.2:
                print(f"\n⚠️  WARNING: Step times INCREASING over time!")
                print(f"   First half avg: {first_half*1000:.2f}ms")
                print(f"   Second half avg: {second_half*1000:.2f}ms")
                print(f"   Increase: {(second_half/first_half - 1)*100:.1f}%")
            else:
                print(f"\n✓ Step times stable (no degradation detected)")
        
        return step_times
    
    def get_summary(self) -> str:
        """Zwróć podsumowanie profilowania."""
        summary = "\n" + "="*70 + "\n"
        summary += "PROFILING SUMMARY\n"
        summary += "="*70 + "\n"
        
        for func_name, times in self.timings.items():
            if times:
                summary += f"\n{func_name}:\n"
                summary += f"  Calls: {len(times)}\n"
                summary += f"  Total: {sum(times):.3f}s\n"
                summary += f"  Avg: {sum(times)/len(times)*1000:.2f}ms\n"
                summary += f"  Min: {min(times)*1000:.2f}ms\n"
                summary += f"  Max: {max(times)*1000:.2f}ms\n"
        
        return summary


class MemoryAnalyzer:
    """Narzędzie do analizy zużycia pamięci."""
    
    @staticmethod
    def get_agent_memory_usage(engine: SimulationEngine) -> Dict:
        """
        Przeanalizuj zużycie pamięci przez agentów.
        
        Sprawdza:
        - Liczbę agentów (żywych i martwych)
        - Rozmiaru struktury danych
        - Efektywności słownika agentów
        """
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        alive_count = sum(1 for c in engine.citizens.values() if c.alive)
        dead_count = len(engine.citizens) - alive_count
        
        # Przybliżony rozmiar jednego agenta
        sample_citizen = next(iter(engine.citizens.values()), None)
        if sample_citizen:
            import sys
            agent_size = sys.getsizeof(sample_citizen)
        else:
            agent_size = 0
        
        total_citizens_size = agent_size * len(engine.citizens)
        
        return {
            "total_citizens": len(engine.citizens),
            "alive_citizens": alive_count,
            "dead_citizens": dead_count,
            "households": len(engine.households),
            "zones": len(engine.zones),
            "approx_agent_size_bytes": agent_size,
            "approx_total_citizens_memory_mb": total_citizens_size / (1024**2),
            "process_rss_mb": memory_info.rss / (1024**2),
            "process_vms_mb": memory_info.vms / (1024**2),
        }
    
    @staticmethod
    def report_memory_usage(engine: SimulationEngine) -> str:
        """Stwórz raport dotyczący zużycia pamięci."""
        usage = MemoryAnalyzer.get_agent_memory_usage(engine)
        
        report = "\n" + "="*70 + "\n"
        report += "MEMORY ANALYSIS REPORT\n"
        report += "="*70 + "\n\n"
        
        report += "AGENT STATISTICS:\n"
        report += "-"*70 + "\n"
        report += f"Total citizens in memory: {usage['total_citizens']:,}\n"
        report += f"  - Alive: {usage['alive_citizens']:,}\n"
        report += f"  - Dead: {usage['dead_citizens']:,}\n"
        report += f"Households: {usage['households']:,}\n"
        report += f"Zones: {usage['zones']:,}\n"
        
        report += "\nMEMORY USAGE:\n"
        report += "-"*70 + "\n"
        report += f"Approx. size per agent: {usage['approx_agent_size_bytes']:,} bytes\n"
        report += f"Approx. total citizens memory: {usage['approx_total_citizens_memory_mb']:.2f} MB\n"
        report += f"Process RSS (resident): {usage['process_rss_mb']:.2f} MB\n"
        report += f"Process VMS (virtual): {usage['process_vms_mb']:.2f} MB\n"
        
        # Ocena efektywności
        report += "\nEFFICIENCY ASSESSMENT:\n"
        report += "-"*70 + "\n"
        
        if usage['dead_citizens'] > usage['alive_citizens'] * 10:
            report += f"⚠️  WARNING: Too many dead citizens kept in memory!\n"
            report += f"   Consider removing dead citizens from memory pool\n"
        else:
            report += f"✓ Dead citizens ratio healthy\n"
        
        # Sprawdzenie czy słownik jest efektywny
        storage_ratio = usage['approx_total_citizens_memory_mb'] / usage['process_rss_mb']
        
        if storage_ratio > 0.5:
            report += f"⚠️  Citizens use {storage_ratio*100:.1f}% of process memory\n"
        else:
            report += f"✓ Citizens use {storage_ratio*100:.1f}% of process memory\n"
        
        return report
    
    @staticmethod
    def analyze_data_structures(engine: SimulationEngine) -> str:
        """Przeanalizuj struktury danych (słownik vs lista)."""
        report = "\n" + "="*70 + "\n"
        report += "DATA STRUCTURES ANALYSIS\n"
        report += "="*70 + "\n\n"
        
        report += f"Citizens storage: Dictionary (citizen.id -> Citizen object)\n"
        report += f"  - Type: {type(engine.citizens).__name__}\n"
        report += f"  - Items: {len(engine.citizens):,}\n"
        report += f"  - Access time: O(1) average, O(n) worst case\n"
        report += f"  - Space efficiency: Good for sparse populations\n\n"
        
        report += f"Households storage: Dictionary (household.id -> Household object)\n"
        report += f"  - Type: {type(engine.households).__name__}\n"
        report += f"  - Items: {len(engine.households):,}\n"
        report += f"  - Access time: O(1) average\n\n"
        
        report += f"Zones storage: Dictionary (zone.id -> Zone object)\n"
        report += f"  - Type: {type(engine.zones).__name__}\n"
        report += f"  - Items: {len(engine.zones):,}\n\n"
        
        report += "RECOMMENDATIONS FOR OPTIMIZATION:\n"
        report += "-"*70 + "\n"
        
        # Sprawdź czy liczba agentów jest duża
        if len(engine.citizens) > 100000:
            report += f"⚠️  Large population ({len(engine.citizens):,} agents)\n"
            report += f"   Consider:\n"
            report += f"   1. Using NumPy arrays for agent attributes\n"
            report += f"   2. Implementing lazy loading\n"
            report += f"   3. Archiving old timesteps\n\n"
        
        report += "Current data structure is dictionary-based (key-value):\n"
        report += "PROS:\n"
        report += "  + Fast lookup by ID\n"
        report += "  + Flexible deletion\n"
        report += "  + Easy to track individual agents\n"
        report += "CONS:\n"
        report += "  - Higher memory overhead than array\n"
        report += "  - Slower iteration for large populations\n"
        report += "  - Dead agents consume memory\n\n"
        
        report += "ALTERNATIVE STRUCTURES:\n"
        report += "  1. List-based: Agent[index] - faster iteration, wasteful for removals\n"
        report += "  2. NumPy array: Vectorized operations, less flexible\n"
        report += "  3. Tagged archive: Keep only alive agents in memory\n"
        
        return report


def print_structure_info():
    """Wypisz informacje o strukturze przechowywania agentów."""
    print("\n" + "="*70)
    print("CURRENT AGENT STORAGE STRUCTURE")
    print("="*70)
    
    info = """
CITIZENS: Dictionary mapping ID -> Citizen object
  - python dict (hash table)
  - O(1) lookup, O(n) iteration
  - Contains both alive and dead citizens
  
HOUSEHOLDS: Dictionary mapping ID -> Household object
  - python dict (hash table)
  - O(1) lookup
  - Groups citizens into family units

ZONES: Dictionary mapping ID -> Zone object
  - python dict (hash table)
  - Contains geographic distribution

CITIZEN CLASS ATTRIBUTES:
  - id: int (unique identifier)
  - sex: str ("male" or "female")
  - age_months: int
  - alive: bool
  - household_id: int
  - zone_id: int
  - diseases: Dict[str, int]
  - risk_factors: Dict[str, int]
  - disability_score: float
  - health_state: str

This structure is efficient for:
  ✓ Individual agent tracking
  ✓ Quick lookup by ID
  ✓ Medical history queries
  
Potential optimizations:
  ✓ Remove dead agents at end of year
  ✓ Use numpy arrays for numerical attributes
  ✓ Vectorize mortality/fertility calculations
"""
    
    print(info)


# ============================================================================
# PRZYKŁAD UŻYCIA
# ============================================================================
if __name__ == "__main__":
    print("Performance Profiling & Memory Analysis Tools")
    print("=" * 70)
    
    # Inicjalizuj silnik symulacji
    print("\nInitializing simulation engine...")
    disease_model = DiseaseModel()
    engine = SimulationEngine(disease_model=disease_model, seed=42)
    
    # Stwórz małą populację test
    print("Creating synthetic population (5000 agents)...")
    engine._create_synthetic_population(5000)
    
    # === MEMORY ANALYSIS ===
    print(MemoryAnalyzer.report_memory_usage(engine))
    print(MemoryAnalyzer.analyze_data_structures(engine))
    
    # === PROFILING ===
    profiler = PerformanceProfiler()
    step_times = profiler.profile_simulation_step(engine, num_steps=20)
    
    # === AFTER SIMULATION ===
    print(MemoryAnalyzer.report_memory_usage(engine))
    
    # === PRINT STRUCTURE INFO ===
    print_structure_info()
