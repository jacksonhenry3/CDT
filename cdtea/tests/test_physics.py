"""Unittests for the physics module"""
import numpy

from cdtea import physics


class TestMoveProbabilities:
    """Tests for move probabilities"""

    def test_increase_probability(self):
        """Test increase move probability"""
        p = physics.increase_probability(1000, 6, 4, 0.7)
        numpy.testing.assert_almost_equal(p, 0.9921784291536654, decimal=10)

    def test_decrease_probability(self):
        """Test decrease move probability"""
        p = physics.decrease_probability(6, 4, 0.7)
        numpy.testing.assert_almost_equal(p, 0.1678127256225397, decimal=10)

    def test_detailed_balance(self):
        """Test that the probabilities obey the detailed balance condition"""
        N = 1000
        nf = 6
        np = 4
        L = 0.7
        p = physics.increase_probability(N, nf, np, L)
        q = physics.decrease_probability(nf, np, L)
        ratio = N / (N + 1) * nf * np * numpy.exp(- 2 * L)
        numpy.testing.assert_almost_equal(p / q, ratio, decimal=10)
