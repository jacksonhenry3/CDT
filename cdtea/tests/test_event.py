"""Unittests for the Event class
"""
from cdtea import event
from cdtea.space_time import SpaceTime
from cdtea.tests import test_space_time


class TestEvent:
    """Tests for Event class"""

    def test_event_init(self):
        """Test event init from spacetime and key"""
        dst = test_space_time.dummy_space_time()
        e = event.Event(space_time=dst, event_key=1)
        assert isinstance(e, event.Event)
        assert id(e.space_time) == id(dst)  # passthru

    def test_event_equality(self):
        """Test Event equality"""
        dst = test_space_time.dummy_space_time()
        e1 = event.Event(space_time=dst, event_key=1)
        e2 = event.Event(space_time=dst, event_key=1)
        assert e1 == e2

        # TODO uncomment the below test once equality defined for SpaceTime
        dst2 = test_space_time.dummy_space_time(2, 2)
        e1_2 = event.Event(space_time=dst2, event_key=1)
        assert e1 != e1_2

    def test_event_repr(self):
        """Test event string representation"""
        dst = test_space_time.dummy_space_time()
        e = event.Event(space_time=dst, event_key=1)
        assert repr(e) == 'Event(ST2, 1)'

    def test_event_pass_thru_getattr(self):
        """Test event getattr behavior for passthru attributes"""
        dst = test_space_time.dummy_space_time(2, 2)
        e0, e1, e2, e3 = event.events(dst, range(4))
        assert e0.right == e1
        assert e1.left == e0
        assert e0.future == [e2, e3]
        assert e3.past == [e0, e1]

    def test_event_safe_getattr(self):
        """Test event getattr behavior for non passthru attributes"""
        dst = test_space_time.dummy_space_time()
        e0 = event.Event(space_time=dst, event_key=0)
        assert isinstance(e0.space_time, SpaceTime)
        assert isinstance(e0.key, int)

    def test_event_hash(self):
        """Test Event Hash"""
        dst_1 = test_space_time.dummy_space_time(2, 2)
        e0_1, *_ = event.events(dst_1, range(4))

        dst_2 = test_space_time.dummy_space_time(2, 2)
        e0_2, *_ = event.events(dst_2, range(4))

        assert hash(e0_1) == hash(e0_2)

    def test_spatial_neighbors(self):
        """Test spatial neighbors"""
        dst = test_space_time.dummy_space_time(3, 3)
        e0, e1, e2, e3, e4, e5, e6, e7, e8 = event.events(dst, range(9))
        assert e0.spatial_neighbors == [e2, e1]

    def test_temporal_neighbors(self):
        """Test temporal neighbors"""
        dst = test_space_time.dummy_space_time(3, 3)
        e0, e1, e2, e3, e4, e5, e6, e7, e8 = event.events(dst, range(9))
        assert e0.temporal_neighbors == [e8, e6, e3, e4]

    def test_neighbors(self):
        """Test neighbors"""
        dst = test_space_time.dummy_space_time(3, 3)
        e0, e1, e2, e3, e4, e5, e6, e7, e8 = event.events(dst, range(9))
        assert e0.neighbors == [e2, e1, e8, e6, e3, e4]

    def test_is_gluing_point(self):
        """Test is gluing point"""
        dst = test_space_time.dummy_space_time(2, 2)
        e1 = event.Event(dst, event.GluingPoint(0))
        e2 = event.Event(dst, 0)
        assert e1.is_gluing_point
        assert not e2.is_gluing_point


class TestEdgeConsistency:
    """Test Edge Consistency Rules"""

    def test_consistent_set_left(self):
        """Check set .left"""
        dst = test_space_time.dummy_space_time(3, 3)
        e0, e1, e2, e3, e4, e5, e6, e7, e8 = event.events(dst, range(9))

        assert e0.right == e1
        event.connect_spatial(e0, e2)
        assert e2.left == e0
        assert e1.left is None

    def test_consistent_set_right(self):
        """Check set .right"""
        dst = test_space_time.dummy_space_time(3, 3)
        e0, e1, e2, e3, e4, e5, e6, e7, e8 = event.events(dst, range(9))

        assert e0.left == e2
        event.connect_spatial(e1, e0)
        assert e1.right == e0
        assert e2.left is None

    def test_consistent_set_past(self):
        """Check set .past"""
        dst = test_space_time.dummy_space_time(3, 3)
        e0, e1, e2, e3, e4, e5, e6, e7, e8 = event.events(dst, range(9))

        assert e0.past == [e8, e6]
        event.connect_temporal(e0, past=[e8, e7])
        assert e0 in e7.future
        assert e0 in e8.future
        assert e0 not in e6.future

    def test_consistent_set_future(self):
        """Check set .future"""
        dst = test_space_time.dummy_space_time(3, 3)
        e0, e1, e2, e3, e4, e5, e6, e7, e8 = event.events(dst, range(9))

        assert e0.future == [e3, e4]
        event.connect_temporal(e0, future=[e4, e5])
        assert e0 in e4.past
        assert e0 in e5.past
        assert e0 not in e3.past

    def test_set_faces(self):
        dst = test_space_time.dummy_space_time(2, 2)
        e0, e1, e2, e3 = event.events(dst)

        assert e0.faces == [frozenset({0, 1, 3}),
                            frozenset({0, 1, 3}),
                            frozenset({0, 2, 3}),
                            frozenset({0, 2, 3}),
                            frozenset({0, 1, 2}),
                            frozenset({0, 1, 2})]
        event.set_faces(e0, [frozenset({0, 1, 3})])
        assert e0.faces == [frozenset({0, 1, 3})]

    def test_temporal_connection_unique(self):
        assert {4, 4} == {4}  # This is how sets remove dups
        assert {4, event.GluingPoint(4)} == {4}  # confirm that Gluinpoint doesn't affect uniqueness


class TestEventUtilities:
    """Test utility functions in event module"""

    def test_event_key(self):
        """Test event_key coercion function"""
        dst = test_space_time.dummy_space_time()
        e0, _ = event.events(dst, [0, 1])
        assert event.event_key(e0) == 0
        assert event.event_key(0) == 0

    def test_events(self):
        """Test multiple event constructor utility"""
        dst = test_space_time.dummy_space_time()
        e0, e1 = event.events(dst, [0, 1])
        assert isinstance(e0, event.Event)
        assert isinstance(e1, event.Event)


class TestGluingPoint:
    """Test gluing point utilities"""

    def test_gluing_point_class(self):
        """Test gluing point class"""
        i = 1
        g = event.GluingPoint(1)
        assert g == i
        assert g in [1]

    def test_coerce_gluing_point(self):
        """Test gluing point coercion"""
        dst_1 = test_space_time.dummy_space_time(2, 2)
        e0_1 = event.Event(dst_1, 0)
        dst_2 = dst_1.pop([e0_1])
        e0_2 = event.Event(dst_2, 0)
        e0_star = event.coerce_gluing_point(dst_1, e0_2)
        assert not isinstance(e0_1.key, event.GluingPoint)
        assert not isinstance(e0_2.key, event.GluingPoint)
        assert isinstance(e0_star.key, event.GluingPoint)
