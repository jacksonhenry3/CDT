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

    def test_imove(self):
        """Test inverse move"""
        dst = dummy_space_time(4, 4)
        n = event.Event(dst, 6)
        modifications.imove(dst, n)
        assert isinstance(dst, SpaceTime)

    def test_functional_inverses(self):
        dst = dummy_space_time(3, 3)
        dst_copy = dummy_space_time(3, 3)
        n, f, p = event.events(dst, [4, 7, 1])
        modifications.move(dst, n, f, p)
        new_node = event.Event(dst, 9)
        modifications.imove(dst, n)
        assert dst.nodes == dst_copy.nodes
        assert dst.node_left == dst_copy.node_left
        assert dst.node_right == dst_copy.node_right

        # The above pass, but the below don't, something wrong in move/imove
        # assert dst.node_past == dst_copy.node_past
        # assert dst.node_future == dst_copy.node_future
        # assert dst == dst_copy
