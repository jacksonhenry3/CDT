"""Unittests for the physics module"""
import numpy

from cdtea import observables, space_time, event, moves


class TestObservables:
    """Tests observables"""

    def test_volume_profile(self):
        """Test volume profile"""
        dst = space_time.generate_flat_spacetime(4, 4)
        n1, f1, p1 = event.events(dst, [12, 0, 11])
        moves.increase(dst, n1, f1, p1)
        n2, f2, p2 = event.events(dst, [13, 1, 9])
        moves.increase(dst, n2, f2, p2)
        vp = observables.volume_profile(dst)
        assert str(vp) == '[4 4 4 6]'
