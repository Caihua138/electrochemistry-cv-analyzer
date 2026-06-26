"""Potential correction module using Nernst equation"""

import numpy as np
from typing import Dict, Tuple


class PotentialCorrector:
    """Convert measured potential to RHE scale using Nernst equation
    
    E_RHE = E_measured + E°_ref + (0.0592/n) * pH
    
    For standard conditions at 25°C with n=2 (most common):
    E_RHE = E_measured + E°_ref + 0.0592 * pH
    """
    
    # Standard electrode potentials (vs SHE at 25°C)
    STANDARD_POTENTIALS = {
        'Hg/HgO': {
            '1M NaOH (pH=14)': 0.945,
            '0.1M KOH (pH=13)': 0.926,
            'saturated KOH': 0.930,
        },
        'Ag/AgCl': {
            '3M KCl': 0.197,
            '1M KCl': 0.235,
            'saturated KCl': 0.197,
        },
        'SCE': {
            'saturated KCl': 0.241,
        },
        'Hg/Hg2SO4': {
            '1M H2SO4': 0.615,
        },
        'SHE': {
            'standard': 0.000,
        }
    }
    
    def __init__(self, temperature: float = 25.0):
        """Initialize potential corrector
        
        Parameters
        ----------
        temperature : float, optional
            Temperature in Celsius (default: 25)
        """
        self.temperature = temperature
        self.F = 96485.33  # Faraday constant (C/mol)
        self.R = 8.314     # Gas constant (J/(mol·K))
        self.n = 2         # Electron transfer number (default for most reactions)
    
    def calculate_slope(self) -> float:
        """Calculate Nernst slope at given temperature
        
        Returns
        -------
        float
            Slope value (mV/pH unit) at temperature T
        """
        T_K = self.temperature + 273.15
        ln_to_log = 2.303  # ln(10)
        slope = (self.R * T_K) / (self.n * self.F * ln_to_log) * 1000  # Convert to mV
        return slope
    
    def correct_to_rhe(self, 
                       measured_potential: float,
                       ref_electrode: str = 'Hg/HgO',
                       ref_condition: str = '1M NaOH (pH=14)',
                       pH: float = 14.0) -> float:
        """Convert measured potential to RHE scale
        
        Parameters
        ----------
        measured_potential : float
            Measured potential (V)
        ref_electrode : str
            Reference electrode type (e.g., 'Hg/HgO', 'Ag/AgCl', 'SCE')
        ref_condition : str
            Condition for reference electrode
        pH : float
            pH of the solution (default: 14 for 1M NaOH)
            
        Returns
        -------
        float
            Potential vs RHE (V)
        """
        # Get standard potential
        try:
            if ref_electrode in self.STANDARD_POTENTIALS:
                if ref_condition in self.STANDARD_POTENTIALS[ref_electrode]:
                    E0_ref = self.STANDARD_POTENTIALS[ref_electrode][ref_condition]
                else:
                    # Use first available condition if specified not found
                    E0_ref = list(self.STANDARD_POTENTIALS[ref_electrode].values())[0]
            else:
                raise ValueError(f"Unknown reference electrode: {ref_electrode}")
        except KeyError:
            raise ValueError(f"Unknown condition: {ref_condition}")
        
        # Nernst equation: E_RHE = E_measured + E°_ref + 0.0592 * pH
        # (assuming n=2 at 25°C)
        slope = 0.0592  # mV/pH at 25°C, converted to V/pH
        E_rhe = measured_potential + E0_ref + slope * pH
        
        return E_rhe
    
    def correct_potential_array(self,
                               potentials: np.ndarray,
                               ref_electrode: str = 'Hg/HgO',
                               ref_condition: str = '1M NaOH (pH=14)',
                               pH: float = 14.0) -> np.ndarray:
        """Convert array of measured potentials to RHE scale
        
        Parameters
        ----------
        potentials : np.ndarray
            Array of measured potentials (V)
        ref_electrode : str
            Reference electrode type
        ref_condition : str
            Condition for reference electrode
        pH : float
            pH of the solution
            
        Returns
        -------
        np.ndarray
            Potentials vs RHE (V)
        """
        vectorized_correct = np.vectorize(
            lambda x: self.correct_to_rhe(x, ref_electrode, ref_condition, pH)
        )
        return vectorized_correct(potentials)
    
    def get_available_electrodes(self) -> Dict:
        """Get list of available reference electrodes and conditions
        
        Returns
        -------
        dict
            Dictionary of available reference electrodes and their conditions
        """
        return self.STANDARD_POTENTIALS.copy()
