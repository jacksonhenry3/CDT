"""Unittests for the Event class
"""
from cdtea import event
from cdtea.SpaceTime import SpaceTime
from tests import test_space_time


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
        # dst2 = test_space_time.dummy_space_time(2, 2)
        # e1_2 = event.Event(space_time=dst2, event_key=1)
        # assert e1 != e1_2

    def test_event_repr(self):
        """Test event string representation"""
        dst = test_space_time.dummy_space_time()
        e = event.Event(space_time=dst, event_key=1)
        assert repr(e) == 'Event(ST2, 1)'

    def test_event_pass_thru_getattr(self):
        dst = test_space_time.dummy_space_time(2, 2)
        e0, e1, e2, e3 = event.events(dst, range(4))
        assert e0.right == e1
        assert e1.left == e0
        assert e0.future == (e2, e3)
        assert e3.past == (e0, e1)

    def test_event_safe_getattr(self):
        dst = test_space_time.dummy_space_time()
        e0 = event.Event(space_time=dst, event_key=0)
        assert isinstance(e0.space_time, SpaceTime)
        assert isinstance(e0.key, int)

    def test_event_pass_thru_setattr(self):
        dst = test_space_time.dummy_space_time(2, 2)
        e0, e1, e2, e3 = event.events(dst, range(4))
        e0.right = e2  # this doesn't make physical sense, but we're testing interface
        assert dst.node_right[0] == 2  # verify that the setattr updated the underlying SpaceTime instance

    def test_event_safe_setattr(self):
        dst = test_space_time.dummy_space_time(2, 2)
        e0, e1, e2, e3 = event.events(dst, range(4))
        e0.key = -1  # this doesn't make physical sense, but we're testing interface
        assert dst.node_right[0] == 1  # verify that the setattr DID NOT update the underlying SpaceTime instance TODO check more attrs / eq


class TestEventUtilities:
    """Test utility functions in event module"""

    def test_event_key(self):
        """Test event_key coercion function"""
        e = event.Event(None, 0)
        assert event.event_key(e) == 0
        assert event.event_key(0) == 0

    def test_events(self):
        """Test multiple event constructor utility"""
        dst = test_space_time.dummy_space_time()
        e0, e1 = event.events(dst, [0, 1])
        assert isinstance(e0, event.Event)
        assert isinstance(e1, event.Event)
