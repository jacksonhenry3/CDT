"""Add Tests for Package-Level Features"""

import cdtea


class TestPackage:
    """Tests for CDTea package"""

    def test_version(self):
        """Test package version, prevents accidental bumps"""
        assert cdtea.__VERSION__ == (0, 0, 1)
        assert cdtea.__version__ == '0.0.1'
