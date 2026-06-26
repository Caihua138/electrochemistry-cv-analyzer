"""Data loader module for CSV and Excel files"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Union, Tuple


class DataLoader:
    """Load CV data from CSV or Excel files"""
    
    def __init__(self):
        self.data = None
        self.filename = None
    
    def load_csv(self, filepath: str) -> pd.DataFrame:
        """Load data from CSV file
        
        Parameters
        ----------
        filepath : str
            Path to CSV file
            
        Returns
        -------
        pd.DataFrame
            DataFrame with columns: T(Seconds), E(V), I(A/cm2)
        """
        try:
            self.data = pd.read_csv(filepath)
            self.filename = Path(filepath).name
            self._validate_columns()
            return self.data
        except Exception as e:
            raise ValueError(f"Error loading CSV file: {e}")
    
    def load_excel(self, filepath: str, sheet_name: int = 0) -> pd.DataFrame:
        """Load data from Excel file
        
        Parameters
        ----------
        filepath : str
            Path to Excel file
        sheet_name : int, optional
            Sheet index (default: 0)
            
        Returns
        -------
        pd.DataFrame
            DataFrame with columns: T(Seconds), E(V), I(A/cm2)
        """
        try:
            self.data = pd.read_excel(filepath, sheet_name=sheet_name)
            self.filename = Path(filepath).name
            self._validate_columns()
            return self.data
        except Exception as e:
            raise ValueError(f"Error loading Excel file: {e}")
    
    def _validate_columns(self):
        """Validate that required columns exist"""
        required_cols = {'T(Seconds)', 'E(V)', 'I(A/cm2)'}
        actual_cols = set(self.data.columns)
        
        # Try to find columns with similar names (case-insensitive)
        normalized_cols = {col.strip().lower(): col for col in actual_cols}
        
        if not required_cols.issubset(actual_cols):
            # Check if columns exist with different formatting
            if len(actual_cols) >= 3:
                # Assume first 3 columns are T, E, I
                self.data.columns = ['T(Seconds)', 'E(V)', 'I(A/cm2)']
            else:
                raise ValueError(
                    f"Expected columns: {required_cols}. Got: {actual_cols}"
                )
    
    def get_data(self) -> pd.DataFrame:
        """Get loaded data
        
        Returns
        -------
        pd.DataFrame
            Loaded data
        """
        if self.data is None:
            raise RuntimeError("No data loaded. Call load_csv() or load_excel() first.")
        return self.data.copy()
    
    def get_filename(self) -> str:
        """Get filename of loaded data"""
        return self.filename
