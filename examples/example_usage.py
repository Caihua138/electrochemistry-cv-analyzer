"""Example usage of the CV Analyzer"""

from pathlib import Path
from src.cv_analyzer import CVAnalyzer
import json


def example_single_file():
    """Analyze a single ORR data file"""
    print("="*60)
    print("Example 1: Analyze Single ORR File")
    print("="*60)
    
    # Initialize analyzer for ORR
    analyzer = CVAnalyzer(
        reaction_type='ORR',
        reference_electrode='Hg/HgO',
        ref_condition='1M NaOH (pH=14)',
        pH=14.0,
        electrode_area=0.1256,  # cm²
        temperature=25.0
    )
    
    # Analyze file
    results = analyzer.analyze_file(
        filepath='data/sample_orr.csv',
        normalize_by_area=True,
        plot=True,
        save_results=True,
        output_dir='results'
    )
    
    # Print results
    print("\nAnalysis Results:")
    print(json.dumps(results, indent=2))
    
    return results


def example_batch_analysis():
    """Batch analyze multiple files"""
    print("\n" + "="*60)
    print("Example 2: Batch Analyze Multiple Files")
    print("="*60)
    
    analyzer = CVAnalyzer(
        reaction_type='ORR',
        reference_electrode='Hg/HgO',
        ref_condition='1M NaOH (pH=14)',
        pH=14.0,
        electrode_area=0.1256
    )
    
    # Batch process
    results_list = analyzer.batch_analyze(
        directory='data/',
        pattern='*.csv',
        normalize_by_area=True,
        plot=True,
        save_results=True,
        output_dir='results'
    )
    
    print(f"\nProcessed {len(results_list)} files")
    
    return results_list


def example_different_reactions():
    """Analyze different reaction types"""
    print("\n" + "="*60)
    print("Example 3: Different Reaction Types")
    print("="*60)
    
    # ORR example (already shown)
    print("\n--- ORR Analysis ---")
    orr_analyzer = CVAnalyzer(
        reaction_type='ORR',
        reference_electrode='Hg/HgO',
        pH=14.0,
        electrode_area=0.1256
    )
    
    # OER example
    print("\n--- OER Analysis ---")
    oer_analyzer = CVAnalyzer(
        reaction_type='OER',
        reference_electrode='Hg/HgO',
        pH=14.0,
        electrode_area=0.0707
    )
    
    # HER example
    print("\n--- HER Analysis ---")
    her_analyzer = CVAnalyzer(
        reaction_type='HER',
        reference_electrode='Ag/AgCl',
        ref_condition='1M KCl',
        pH=1.0,
        electrode_area=0.0707
    )
    
    print("\nAnalyzers configured for different reaction types.")


def example_potential_correction():
    """Demonstrate potential correction"""
    print("\n" + "="*60)
    print("Example 4: Potential Correction (Nernst Equation)")
    print("="*60)
    
    from src.potential_corrector import PotentialCorrector
    
    corrector = PotentialCorrector(temperature=25.0)
    
    # Example: Hg/HgO reference in 1M NaOH (pH=14)
    measured_E = 0.155  # V
    E_rhe = corrector.correct_to_rhe(
        measured_potential=measured_E,
        ref_electrode='Hg/HgO',
        ref_condition='1M NaOH (pH=14)',
        pH=14.0
    )
    
    print(f"\nMeasured potential: {measured_E:.3f} V (Hg/HgO)")
    print(f"Corrected potential: {E_rhe:.3f} V vs RHE")
    print(f"Correction: E_RHE = E_measured + E°_ref + 0.0592*pH")
    print(f"E_RHE = {measured_E} + 0.945 + 0.0592*14 = {E_rhe:.3f} V")
    
    # Show available electrodes
    print("\nAvailable reference electrodes:")
    available = corrector.get_available_electrodes()
    for electrode, conditions in available.items():
        print(f"  {electrode}:")
        for condition, E0 in conditions.items():
            print(f"    - {condition}: E° = {E0:.3f} V vs SHE")


if __name__ == '__main__':
    # Run examples
    example_potential_correction()
    example_different_reactions()
    
    # Uncomment to run actual analysis (requires data files)
    # example_single_file()
    # example_batch_analysis()
    
    print("\n" + "="*60)
    print("Examples completed!")
    print("="*60)
