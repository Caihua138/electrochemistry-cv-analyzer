"""Parameter calculator for electrochemical analysis"""

import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
from scipy.optimize import minimize_scalar, linear_sum_squares
from typing import Dict, Tuple, Optional
import warnings


class ParameterCalculator:
    """Calculate electrochemical parameters from CV data"""
    
    def __init__(self, reaction_type: str = 'ORR'):
        """Initialize calculator
        
        Parameters
        ----------
        reaction_type : str
            Type of reaction: 'ORR', 'OER', or 'HER'
        """
        self.reaction_type = reaction_type.upper()
        if self.reaction_type not in ['ORR', 'OER', 'HER']:
            raise ValueError(f"Unknown reaction type: {reaction_type}")
    
    def calculate_onset_potential(self,
                                  potentials: np.ndarray,
                                  currents: np.ndarray,
                                  threshold: float = -0.1) -> Tuple[float, int]:
        """Calculate onset potential
        
        For ORR: onset when j = -0.1 mA/cm²
        For OER: onset when current significantly increases
        For HER: onset when current significantly increases
        
        Parameters
        ----------
        potentials : np.ndarray
            Potential values (V vs RHE)
        currents : np.ndarray
            Current density values (mA/cm²)
        threshold : float
            Current threshold for onset (mA/cm²)
            
        Returns
        -------
        tuple
            (onset_potential, index)
        """
        if self.reaction_type == 'ORR':
            # Find potential where j = threshold (-0.1 mA/cm²)
            if np.all(currents > threshold):
                warnings.warn("No current reaches threshold for ORR onset")
                return None, None
            
            # Find closest point to threshold
            idx = np.argmin(np.abs(currents - threshold))
            onset_E = potentials[idx]
            return onset_E, idx
        
        elif self.reaction_type in ['OER', 'HER']:
            # For OER/HER: find where current starts to significantly increase
            # Use gradient to find inflection point or onset
            if len(currents) < 3:
                return None, None
            
            # Calculate derivative
            dj_dE = np.gradient(currents, potentials)
            
            # Find point with maximum positive derivative (for OER) or minimum (for HER)
            if self.reaction_type == 'OER':
                idx = np.argmax(dj_dE)
            else:  # HER
                idx = np.argmin(dj_dE)
            
            onset_E = potentials[idx]
            return onset_E, idx
    
    def calculate_tafel_slope(self,
                             potentials: np.ndarray,
                             currents: np.ndarray,
                             onset_idx: Optional[int] = None,
                             auto_range: bool = True) -> Tuple[float, float, Tuple[int, int]]:
        """Calculate Tafel slope
        
        η = a + b*log10|j|
        where b is Tafel slope (mV/dec)
        
        Parameters
        ----------
        potentials : np.ndarray
            Potential values (V vs RHE)
        currents : np.ndarray
            Current density values (mA/cm²)
        onset_idx : int, optional
            Index of onset potential
        auto_range : bool
            Whether to automatically identify linear region
            
        Returns
        -------
        tuple
            (tafel_slope_mV_dec, r_squared, (start_idx, end_idx))
        """
        # Convert to overpotential and absolute current
        if onset_idx is None:
            onset_idx = 0
        
        # Get data from onset onwards
        E_range = potentials[onset_idx:]
        j_range = np.abs(currents[onset_idx:])
        
        # Remove zero or negative currents
        valid_mask = j_range > 0
        if np.sum(valid_mask) < 3:
            warnings.warn("Not enough valid data points for Tafel slope")
            return None, None, (None, None)
        
        E_range = E_range[valid_mask]
        j_range = j_range[valid_mask]
        
        if auto_range:
            # Find linear region: use points where |dlog(j)/dlog(E)| is relatively constant
            log_j = np.log10(j_range)
            
            # Try different window sizes and find best linear fit
            best_slope = None
            best_r2 = -np.inf
            best_range = (0, len(log_j))
            
            # Minimum window size
            min_points = max(3, int(0.2 * len(log_j)))
            
            for start in range(len(log_j) - min_points):
                for end in range(start + min_points, len(log_j) + 1):
                    E_subset = E_range[start:end]
                    log_j_subset = log_j[start:end]
                    
                    # Linear fit: log_j = a + b*E
                    coeffs = np.polyfit(E_subset, log_j_subset, 1)
                    
                    # Calculate R²
                    y_pred = np.polyval(coeffs, E_subset)
                    ss_res = np.sum((log_j_subset - y_pred) ** 2)
                    ss_tot = np.sum((log_j_subset - np.mean(log_j_subset)) ** 2)
                    r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
                    
                    if r2 > best_r2 and r2 > 0.95:  # Only accept high R²
                        best_r2 = r2
                        best_slope = coeffs[0] * 1000  # Convert to mV/dec
                        best_range = (onset_idx + start, onset_idx + end)
            
            if best_slope is None:
                # Fallback: use entire range
                log_j = np.log10(j_range)
                coeffs = np.polyfit(E_range, log_j, 1)
                best_slope = coeffs[0] * 1000
                y_pred = np.polyval(coeffs, E_range)
                ss_res = np.sum((log_j - y_pred) ** 2)
                ss_tot = np.sum((log_j - np.mean(log_j)) ** 2)
                best_r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
                best_range = (onset_idx, onset_idx + len(log_j))
        else:
            # Use entire range
            log_j = np.log10(j_range)
            coeffs = np.polyfit(E_range, log_j, 1)
            best_slope = coeffs[0] * 1000  # Convert to mV/dec
            y_pred = np.polyval(coeffs, E_range)
            ss_res = np.sum((log_j - y_pred) ** 2)
            ss_tot = np.sum((log_j - np.mean(log_j)) ** 2)
            best_r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            best_range = (onset_idx, len(currents))
        
        return best_slope, best_r2, best_range
    
    def calculate_limited_current_density(self,
                                         currents: np.ndarray,
                                         range_percent: float = 0.1) -> float:
        """Calculate limited current density
        
        Average of maximum current in the last 10% of data
        
        Parameters
        ----------
        currents : np.ndarray
            Current density values (mA/cm²)
        range_percent : float
            Fraction of data to average from the end (default: 0.1)
            
        Returns
        -------
        float
            Limited current density (mA/cm²)
        """
        # Use last range_percent of data
        n_points = int(len(currents) * range_percent)
        n_points = max(n_points, 1)
        
        # For ORR, limit current is negative
        # Take the most negative value
        if self.reaction_type == 'ORR':
            limit_current = np.min(currents[-n_points:])
        else:
            # For OER/HER, take the maximum
            limit_current = np.max(currents[-n_points:])
        
        return limit_current
    
    def calculate_on_half_potential(self,
                                    potentials: np.ndarray,
                                    currents: np.ndarray) -> Tuple[float, int]:
        """Calculate potential at 50% of limited current density
        
        Parameters
        ----------
        potentials : np.ndarray
            Potential values (V vs RHE)
        currents : np.ndarray
            Current density values (mA/cm²)
            
        Returns
        -------
        tuple
            (on_half_potential, index)
        """
        if self.reaction_type != 'ORR':
            warnings.warn("On-Half Potential is primarily for ORR analysis")
        
        # Get limited current
        limited_current = self.calculate_limited_current_density(currents)
        
        # Find potential at 50% of limited current
        target_current = limited_current * 0.5
        
        # Find closest point
        idx = np.argmin(np.abs(currents - target_current))
        on_half_E = potentials[idx]
        
        return on_half_E, idx
    
    def calculate_overpotential(self,
                               potential: float,
                               theoretical_potential: float = 1.23) -> float:
        """Calculate overpotential (for OER/HER)
        
        Parameters
        ----------
        potential : float
            Applied potential (V vs RHE)
        theoretical_potential : float
            Theoretical/equilibrium potential (V vs RHE)
            For OER: 1.23 V
            For HER: 0.0 V
            
        Returns
        -------
        float
            Overpotential (V), absolute value
        """
        eta = abs(potential - theoretical_potential)
        return eta
