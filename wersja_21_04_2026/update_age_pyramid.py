"""
Aktualizacja piramidy wieku z optymalnymi parametrami z GridSearch'a
"""

from simulation_engine import SimulationEngine
from disease_model import DiseaseModel
from visualization import SimulationVisualizer


def update_age_pyramid():
    """
    Uruchom symulację z parametrami z gridsearch'a i wygeneruj nową piramidę wieku
    50 lat, 50,000 agentów
    """
    print("\n" + "="*70)
    print("AKTUALIZACJA PIRAMIDY WIEKU")
    print("Parametry z Grid Search: Fertility=2.0, Mortality=0.5")
    print("Symulacja: 50 lat z populacją 5000 obywateli")
    print("="*70 + "\n")
    
    # Inne parametry znalezione w gridsearch'u
    fertility_multiplier = 2.0
    mortality_multiplier = 0.5
    
    # Inicjalizuj model choroby
    disease_model = DiseaseModel()
    
    # Stwórz silnik symulacji
    engine = SimulationEngine(disease_model=disease_model, seed=42)
    
    # Ustaw mnożniki demograficzne
    engine.fertility_rate = fertility_multiplier
    engine.mortality_multiplier = mortality_multiplier
    engine.household_split_probability = 0.001
    
    # Wygeneruj większą populację dla bardziej reprezentatywnej piramidy
    print("📊 Generowanie populacji syntetycznej (50,000 obywateli)...")
    engine._create_synthetic_population(50000)
    
    # Uruchom symulację na 50 lat
    print("🔄 Uruchamianie symulacji na 50 lat...")
    engine.run(months=600)  # 50 lat
    
    # Stwórz wizualizer
    visualizer = SimulationVisualizer(engine.yearly_stats)
    
    # Wygeneruj nową piramidę wieku
    print("🎨 Generowanie piramidy wieku...")
    visualizer.plot_interactive_age_pyramid("piramida_wieku_rok_50_gridsearch.html")
    
    # Wygeneruj animowaną piramidę
    print("🎬 Generowanie animowanej piramidy wieku...")
    visualizer.create_animated_age_pyramid("piramida_wieku_animowana_50lat_gridsearch.html")
    
    # Wypisz statystyki finalne
    final_year = max(engine.yearly_stats.keys())
    final_stats = engine.yearly_stats[final_year]
    
    # Zsumuj ludność z piramidy wieku
    age_pyramid = final_stats.get("age_pyramid", {})
    total_population = sum(
        age_pyramid[age_bin].get("male", 0) + age_pyramid[age_bin].get("female", 0)
        for age_bin in age_pyramid
    )
    
    print("\n" + "="*70)
    print("STATYSTYKI FINALNE - ROK " + str(final_year))
    print("="*70)
    print(f"Populacja początkowa: 50,000")
    print(f"Populacja końcowa: {total_population}")
    print(f"Liczba gospodarstw domowych: {final_stats.get('households', 'N/A')}")
    print(f"Średni wiek populacji: {final_stats.get('avg_age', 'N/A')} lat")
    print("="*70 + "\n")
    
    # Pokaż rozkład wieku
    pyramid = age_pyramid
    if pyramid:
        print("ROZKŁAD WIEKU:")
        print("-" * 50)
        
        # Custom sort: najpierw grupy normalne (0-4, 5-9, ...), potem stare (90-94, 95-99, 100+)
        def sort_age_bin(age_bin):
            if age_bin == "100+":
                return (100, 0)
            elif age_bin.startswith("9"):  # 90-94, 95-99
                start = int(age_bin.split("-")[0])
                return (start, 0)
            else:  # 0-4, 5-9, etc.
                start = int(age_bin.split("-")[0])
                return (start, 0)
        
        for age_bin in sorted(pyramid.keys(), key=sort_age_bin):
            male = pyramid[age_bin].get("male", 0)
            female = pyramid[age_bin].get("female", 0)
            total = male + female
            if total_population > 0:
                pct = (total / total_population) * 100
            else:
                pct = 0
            print(f"  {age_bin:6s} | M: {male:4d} | K: {female:4d} | Razem: {total:4d} ({pct:5.1f}%)")
        print("-" * 50 + "\n")


if __name__ == "__main__":
    try:
        update_age_pyramid()
        print("✅ Piramida wieku została zaktualizowana!")
    except Exception as e:
        print(f"❌ Błąd: {e}")
        import traceback
        traceback.print_exc()
