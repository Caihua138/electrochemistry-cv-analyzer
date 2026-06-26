"""Main CV analyzer module"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional
import json
from datetime import datetime

from src.data_loader import DataLoader
from src.potential_corrector import PotentialCorrector
from src.parameter_calculator import ParameterCalculator
from src.plotter import CVPlotter


class CVAnalyzer:
    """Main analyzer for electrochemical CV data"""
    
    def __init__(self,
                 reaction_type: str = 'ORR',
                 reference_electrode: str = 'Hg/HgO',
                 ref_condition: str = '1M NaOH (pH=14)',
                 pH: float = 14.0,
                 electrode_area: float = 0.1256,
                 temperature: float = 25.0):
        """Initialize analyzer
        
        Parameters
        ----------
        reaction_type : str
            'ORR', 'OER', or 'HER'
        reference_electrode : str
            Type of reference electrode
        ref_condition : str
            Condition for reference electrode
        pH : float
            pH of solution
        electrode_area : float
            Electrode area (cm²)
        temperature : float
            Temperature (°C)
        """
        self.reaction_type = reaction_type.upper()
        self.ref_electrode = reference_electrode
        self.ref_condition = ref_condition
        self.pH = pH
        self.electrode_area = electrode_area
        self.temperature = temperature
        
        self.loader = DataLoader()
        self.corrector = PotentialCorrector(temperature=temperature)
        self.calculator = ParameterCalculator(reaction_type=reaction_type)
        self.plotter = CVPlotter(reaction_type=reaction_type)
        
        self.results = None
    
    def analyze_file(self,
                    filepath: str,
                    normalize_by_area: bool = True,
                    plot: bool = True,
                    save_results: bool = True,
                    output_dir: str = 'results') -> Dict:
        """Analyze single CV file
        
        Parameters
        ----------
        filepath : str
            Path to CSV or Excel file
        normalize_by_area : bool
            Whether to normalize current by electrode area
        plot : bool
            Whether to generate plots
        save_results : bool
            Whether to save results to JSON
        output_dir : str
            Directory to save results
            
        Returns
        -------
        dict
            Analysis results
        """
        # Load data
        filepath = Path(filepath)
        if filepath.suffix.lower() == '.csv':
            data = self.loader.load_csv(str(filepath))
        else:
            data = self.loader.load_excel(str(filepath))
        
        # Extract data
        potentials_measured = data['E(V)'].values
        currents_raw = data['I(A/cm2)'].values
        
        # Correct potentials to RHE
        potentials_rhe = self.corrector.correct_potential_array(
            potentials_measured,
            ref_electrode=self.ref_electrode,
            ref_condition=self.ref_condition,
            pH=self.pH
        )
        
        # Normalize current if needed
        if normalize_by_area:
            currents = currents_raw * 1000 / self.electrode_area  # Convert A to mA, normalize by area
        else:
            currents = currents_raw * 1000  # Convert A to mA
        
        # Only take first half (forward scan)
        n_half = len(potentials_rhe) // 2
        potentials_rhe = potentials_rhe[:n_half]
        currents = currents[:n_half]
        
        # Calculate parameters
        onset_E, onset_idx = self.calculator.calculate_onset_potential(
            potentials_rhe, currents
        )
        
        tafel_slope, r2_tafel, tafel_range = self.calculator.calculate_tafel_slope(
            potentials_rhe, currents, onset_idx=onset_idx
        )
        
        if self.reaction_type == 'ORR':
            limited_current = self.calculator.calculate_limited_current_density(currents)
            on_half_E, _ = self.calculator.calculate_on_half_potential(
                potentials_rhe, currents
            )
        else:
            limited_current = None
            on_half_E = None
        
        # Compile results
        self.results = {
            'filename': filepath.name,
            'reaction_type': self.reaction_type,
            'electrode_area_cm2': self.electrode_area,
            'reference_electrode': f"{self.ref_electrode} ({self.ref_condition})",
            'pH': self.pH,
            'temperature_C': self.temperature,
            'potential_correction_V': self.corrector.STANDARD_POTENTIALS[
                self.ref_electrode][self.ref_condition],
            'parameters': {
                'onset_potential_V_vs_RHE': float(onset_E) if onset_E is not None else None,
                'tafel_slope_mV_dec': float(tafel_slope) if tafel_slope is not None else None,
                'tafel_slope_r_squared': float(r2_tafel) if r2_tafel is not None else None,
            },
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        # Add ORR-specific parameters
        if self.reaction_type == 'ORR':
            self.results['parameters']['limited_current_density_mA_cm2'] = float(limited_current) if limited_current is not None else None
            self.results['parameters']['on_half_potential_V_vs_RHE'] = float(on_half_E) if on_half_E is not None else None
        
        # Save results
        if save_results:
            self._save_results(output_dir)
        
        # Generate plots
        if plot:
            self.plotter.plot_cv(
                potentials_rhe, currents,
                onset_E, tafel_range,
                save_path=Path(output_dir) / filepath.stem if save_results else None
            )
        
        return self.results
    
    def batch_analyze(self,
                     directory: str,
                     pattern: str = '*.csv',
                     **kwargs) -> List[Dict]:
        """Analyze multiple files in directory
        
        Parameters
        ----------
        directory : str
            Directory containing CV files
        pattern : str
            File pattern to match (default: '*.csv')
        **kwargs
            Additional arguments for analyze_file()
            
        Returns
        -------
        list
            List of analysis results
        """
        directory = Path(directory)
        results_list = []
        
        files = list(directory.glob(pattern))
        if not files:
            print(f"No files matching {pattern} found in {directory}")
            return results_list
        
        print(f"Processing {len(files)} files...")
        for i, filepath in enumerate(files, 1):
            try:
                print(f"[{i}/{len(files)}] Processing {filepath.name}...")
                result = self.analyze_file(str(filepath), **kwargs)
                results_list.append(result)
            except Exception as e:
                print(f"Error processing {filepath.name}: {e}")
        
        return results_list
    
    def _save_results(self, output_dir: str = 'results'):
        """Save results to JSON file"""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        filename = output_dir / f"{Path(self.results['filename']).stem}_results.json"
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"Results saved to {filename}")
