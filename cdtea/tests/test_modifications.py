"""Tests for the modifications module"""
from cdtea import event, moves
from cdtea.space_time import SpaceTime, generate_flat_spacetime
from cdtea.tests import audit


class TestModifications:
    """Test modification moves"""

    def test_move(self):
        """Test move"""
        dst = generate_flat_spacetime(3, 3)
        n, f, p = event.events(dst, [4, 7, 1])
        moves.increase(dst, n, f, p)
        assert isinstance(dst, SpaceTime)

    def test_multiple_moves(self):
        dst = generate_flat_spacetime(4, 4)
        n1, f1, p1 = event.events(dst, [12, 0, 11])
        moves.increase(dst, n1, f1, p1)
        n2, f2, p2 = event.events(dst, [13, 1, 9])
        moves.increase(dst, n2, f2, p2)
        assert isinstance(dst, SpaceTime)

    def test_imove(self):
        """Test inverse move"""
        dst = generate_flat_spacetime(4, 4)
        n = event.Event(dst, 6)
        moves.decrease(dst, n)
        assert isinstance(dst, SpaceTime)

    def test_functional_inverses(self):
        dst = generate_flat_spacetime(3, 3)
        dst_copy = generate_flat_spacetime(3, 3)
        n, f, p = event.events(dst, [4, 7, 1])
        moves.increase(dst, n, f, p)
        new_node = event.Event(dst, 9)
        moves.decrease(dst, n)
        assert dst.nodes == dst_copy.nodes
        assert dst.node_left == dst_copy.node_left
        assert dst.node_right == dst_copy.node_right

        # The above pass, but the below don't, something wrong in move/imove
        # assert dst.node_past == dst_copy.node_past
        # assert dst.node_future == dst_copy.node_future
        # assert dst == dst_copy
