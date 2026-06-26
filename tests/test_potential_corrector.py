"""Tests for potential corrector"""

import numpy as np
from src.potential_corrector import PotentialCorrector


def test_nernst_equation():
    """Test Nernst equation calculation"""
    corrector = PotentialCorrector(temperature=25.0)
    
    # Test case: Hg/HgO in 1M NaOH (pH=14)
    measured_E = 0.155  # V
    E_rhe = corrector.correct_to_rhe(
        measured_potential=measured_E,
        ref_electrode='Hg/HgO',
        ref_condition='1M NaOH (pH=14)',
        pH=14.0
    )
    
    # Expected: 0.155 + 0.945 + 0.0592*14 = 1.1
    expected = 0.155 + 0.945 + 0.0592 * 14
    assert np.isclose(E_rhe, expected, atol=0.01), f"Expected {expected}, got {E_rhe}"
    print(f"✓ Nernst equation test passed: {E_rhe:.3f} V")


def test_potential_array():
    """Test array correction"""
    corrector = PotentialCorrector()
    potentials = np.array([0.155, 0.156, 0.157])
    
    E_rhe_array = corrector.correct_potential_array(
        potentials,
        ref_electrode='Hg/HgO',
        ref_condition='1M NaOH (pH=14)',
        pH=14.0
    )
    
    assert len(E_rhe_array) == len(potentials)
    assert np.all(E_rhe_array > potentials)  # Should increase
    print(f"✓ Array correction test passed")


if __name__ == '__main__':
    test_nernst_equation()
    test_potential_array()
    print("\nAll tests passed!")
