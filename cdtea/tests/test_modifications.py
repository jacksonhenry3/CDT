"""Tests for the modifications module"""
from cdtea import event, modifications
from cdtea.space_time import SpaceTime
from cdtea.tests.test_space_time import dummy_space_time


class TestModifications:
    """Test modification moves"""

    def test_move(self):
        """Test move"""
        dst = dummy_space_time(3, 3)
        n, f, p = event.events(dst, [4, 7, 1])
        modifications.move(dst, n, f, p)
        assert isinstance(dst, SpaceTime)
