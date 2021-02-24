"""Tests for auditing tools"""
from cdtea import space_time
from cdtea.tests import audit


class TestTestingUtils:
    """Tests for the helper test functions"""

    def test_find_duplicate_temp_conn(self):
        """Test duplicate connection finder"""
        valid_cdt = space_time.generate_flat_spacetime(10, 10)
        invalid_cdt = space_time.generate_flat_spacetime(10, 10)
        invalid_cdt.node_future[0] = [10, 19, 19]
        valid_dups = audit.find_duplicate_temporal_connections(valid_cdt)
        assert valid_dups is None
        invalid_dups = audit.find_duplicate_temporal_connections(invalid_cdt)
        assert invalid_dups is not None
        assert invalid_dups == [(0, 'future', [10, 19, 19])]

    def test_ranges(self):
        """Test ranges utility"""
        rs = list(audit.ranges([0, 1, 2, 3, 4, 7, 8, 9, 11]))
        assert rs == [(0, 4), (7, 9), (11, 11)]

    def test_diff(self):
        """Test diff tool"""
        cdt1 = space_time.generate_flat_spacetime(3, 3)
        cdt2 = space_time.generate_flat_spacetime(3, 4)
        diff = audit.spacetime_diff(cdt1, cdt2)
        assert isinstance(diff, audit.DiffSummary)

    def test_diff_summary(self):
        """Test diff tool summary"""
        cdt1 = space_time.generate_flat_spacetime(3, 3)
        cdt2 = space_time.generate_flat_spacetime(3, 4)
        diff = audit.spacetime_diff(cdt1, cdt2)
        summary = audit.format_diff(diff)
        assert isinstance(summary, str)

