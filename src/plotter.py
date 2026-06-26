"""Plotting module for CV analysis visualization"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Optional, Tuple
import warnings


class CVPlotter:
    """Generate visualizations for CV data"""
    
    def __init__(self, reaction_type: str = 'ORR', figsize: Tuple = (12, 8)):
        """Initialize plotter
        
        Parameters
        ----------
        reaction_type : str
            Type of reaction
        figsize : tuple
            Figure size (width, height)
        """
        self.reaction_type = reaction_type.upper()
        self.figsize = figsize
        self.dpi = 300
    
    def plot_cv(self,
               potentials: np.ndarray,
               currents: np.ndarray,
               onset_potential: Optional[float] = None,
               tafel_range: Optional[Tuple[int, int]] = None,
               save_path: Optional[str] = None,
               show: bool = True):
        """Plot CV curve with annotations
        
        Parameters
        ----------
        potentials : np.ndarray
            Potential values (V vs RHE)
        currents : np.ndarray
            Current density values (mA/cm²)
        onset_potential : float, optional
            Onset potential to mark
        tafel_range : tuple, optional
            (start_idx, end_idx) for Tafel region
        save_path : str, optional
            Path to save figure
        show : bool
            Whether to show plot
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=self.figsize)
        
        # Plot 1: Linear CV curve
        ax1.plot(potentials, currents, 'b-', linewidth=2, label='CV curve')
        ax1.set_xlabel('Potential (V vs RHE)', fontsize=12)
        ax1.set_ylabel('Current Density (mA/cm²)', fontsize=12)
        ax1.set_title(f'{self.reaction_type} - Linear Plot', fontsize=13, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.axhline(y=0, color='k', linestyle='--', alpha=0.3)
        
        # Mark onset potential
        if onset_potential is not None:
            ax1.axvline(x=onset_potential, color='r', linestyle='--', 
                       linewidth=2, alpha=0.7, label=f'Onset: {onset_potential:.3f} V')
            ax1.legend(fontsize=11)
        
        # Plot 2: Tafel plot (overpotential vs log|j|)
        if self.reaction_type == 'ORR':
            # Convert to absolute values for Tafel
            abs_currents = np.abs(currents)
            valid_mask = abs_currents > 0
            
            if np.sum(valid_mask) > 0:
                potentials_valid = potentials[valid_mask]
                currents_valid = abs_currents[valid_mask]
                
                ax2.semilogy(potentials_valid, currents_valid, 'bo-', 
                           linewidth=2, markersize=4, label='ORR')
                
                # Mark Tafel region if provided
                if tafel_range is not None and tafel_range[0] is not None:
                    start_idx, end_idx = tafel_range
                    tafel_E = potentials_valid[max(0, start_idx):min(len(potentials_valid), end_idx)]
                    tafel_j = currents_valid[max(0, start_idx):min(len(currents_valid), end_idx)]
                    
                    if len(tafel_E) > 1:
                        ax2.semilogy(tafel_E, tafel_j, 'r-', linewidth=3, 
                                   label='Tafel region', alpha=0.7)
            
            ax2.set_ylabel('|Current Density| (mA/cm²)', fontsize=12)
        else:
            # For OER/HER, plot normal Tafel
            abs_currents = np.abs(currents)
            valid_mask = abs_currents > 0
            
            if np.sum(valid_mask) > 0:
                potentials_valid = potentials[valid_mask]
                currents_valid = abs_currents[valid_mask]
                
                ax2.loglog(potentials_valid, currents_valid, 'go-',
                         linewidth=2, markersize=4, label=self.reaction_type)
                ax2.set_ylabel('|Current Density| (mA/cm²)', fontsize=12)
            
            if tafel_range is not None and tafel_range[0] is not None:
                start_idx, end_idx = tafel_range
                tafel_E = potentials_valid[max(0, start_idx):min(len(potentials_valid), end_idx)]
                tafel_j = currents_valid[max(0, start_idx):min(len(currents_valid), end_idx)]
                
                if len(tafel_E) > 1:
                    ax2.loglog(tafel_E, tafel_j, 'r-', linewidth=3,
                             label='Tafel region', alpha=0.7)
        
        ax2.set_xlabel('Potential (V vs RHE)', fontsize=12)
        ax2.set_title(f'{self.reaction_type} - Tafel Plot', fontsize=13, fontweight='bold')
        ax2.grid(True, alpha=0.3, which='both')
        ax2.legend(fontsize=11)
        
        plt.tight_layout()
        
        if save_path:
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(f"{save_path}_cv_analysis.png", dpi=self.dpi, bbox_inches='tight')
            print(f"Plot saved to {save_path}_cv_analysis.png")
        
        if show:
            plt.show()
        else:
            plt.close()
    
    def plot_comparison(self,
                       potentials_list: list,
                       currents_list: list,
                       labels: list,
                       save_path: Optional[str] = None,
                       show: bool = True):
        """Compare multiple CV curves
        
        Parameters
        ----------
        potentials_list : list
            List of potential arrays
        currents_list : list
            List of current arrays
        labels : list
            Labels for each curve
        save_path : str, optional
            Path to save figure
        show : bool
            Whether to show plot
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        colors = plt.cm.tab10(np.linspace(0, 1, len(potentials_list)))
        
        for i, (potentials, currents, label) in enumerate(zip(potentials_list, currents_list, labels)):
            ax.plot(potentials, currents, color=colors[i], linewidth=2.5, 
                   marker='o', markersize=4, label=label, alpha=0.8)
        
        ax.set_xlabel('Potential (V vs RHE)', fontsize=12)
        ax.set_ylabel('Current Density (mA/cm²)', fontsize=12)
        ax.set_title(f'{self.reaction_type} - Comparison', fontsize=13, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.axhline(y=0, color='k', linestyle='--', alpha=0.3)
        ax.legend(fontsize=11, loc='best')
        
        plt.tight_layout()
        
        if save_path:
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(f"{save_path}_comparison.png", dpi=self.dpi, bbox_inches='tight')
            print(f"Comparison plot saved to {save_path}_comparison.png")
        
        if show:
            plt.show()
        else:
            plt.close()
