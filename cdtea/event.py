"""This module defines properties related to nodes in spacetime as well as their manipulation. Most
non-trivial operations are reserved for the SpaceTime object, and the Node class is largely a syntactic
sugar for code readability
"""

import typing
from collections import Iterable

PASS_THRU_ATTRS = {
    # Mapping of attribute name in Node object and corresponding lookup-dict in SpaceTime object
    # NOTE: this depends on implementation details of SpaceTime class, and should be updated in tandem
    'left': 'node_left',
    'right': 'node_right',
    'past': 'node_past',
    'future': 'node_future',
    'faces': 'faces_containing'
}
EVENT_RETURNING_ATTRS = ('left', 'right', 'past', 'future')


class Event:
    """A light-weight representation of a node in a SpaceTime. Since the SpaceTime contains
    lookup-dicts of all relevant node-edge relationships, the Node class serves as a syntactic
    sugar for passing between a particular node identifier and various feature lookups in the
    SpaceTime object.
    """

    def __init__(self, space_time, event_key):
        """Create an Event isntance

        Args:
            space_time:
                SpaceTime, the spacetime object
            event_key:
                int, the Event label
        """
        self.space_time = space_time
        if isinstance(event_key, Event):
            # TODO check space_time equivalence
            event_key = event_key.key
        # Check that event exists in space_time (consistency)
        if space_time.closed and event_key not in space_time.nodes:
            raise ValueError('Event Key {:d} not defined in spacetime: {}'.format(event_key, space_time))
        self.key = event_key

    def __eq__(self, other):
        """Equality comparison operator

        Args:
            other:
                Any, if an Event instance compare for equality

        Returns:
            bool, True if equivalent events, False otherwise
        """
        # TODO add "and other.space_time == self.space_time" once __eq__ defined for SpaceTime
        return isinstance(other, Event) and other.key == self.key

    def __getattr__(self, item):
        """Override the behavior of attribute lookup ONLY for the case of pass-thru attributes,
        which are defined above in PASS_THRU_ATTRIBUTES. for these attributes only, the getattr
        call will be redirected to the underlying SpaceTime object from which the key originates

        Args:
            item:
                str, the name of the attribute to get
        """
        if item in PASS_THRU_ATTRS:
            value = getattr(self.space_time, PASS_THRU_ATTRS[item])[self.key]
            if item in EVENT_RETURNING_ATTRS:
                if isinstance(value, Iterable):
                    return [Event(space_time=self.space_time, event_key=v) for v in value]
                return Event(space_time=self.space_time, event_key=value)
            return value
        return super(Event, self).__getattribute__(item)

    def __hash__(self):
        """Make Event hashable

        Returns:
            int, the has value of the Event
        """
        # TODO add spacetime hash
        return hash(('Event', self.key))

    def __repr__(self):
        """Define convenient representation for events"""
        # TODO update this to use the SpaceTime repr, now it's just using STN
        # TODO update this to include a time coordinate if possible
        return 'Event(ST{:d}, {:d})'.format(len(self.space_time.nodes), self.key)

    def __setattr__(self, key, value):
        """Override the behavior of attribute setting ONLY for the case of pass-thru attributes,
        which are defined above in PASS_THRU_ATTRIBUTES. for these attributes only, the setattr
        call will be redirected to the underlying SpaceTime object from which the key originates

        Args:
            key:
                str, the name of the attribute to set
            value:
                Any, if an Event instance and key is a pass-thru attr, value will be coerced to int before
                assignment to corresponding SpaceTime attribute lookup dict
        """
        if key in PASS_THRU_ATTRS:
            value = [event_key(v) for v in value] if isinstance(value, Iterable) else event_key(value)
            getattr(self.space_time, PASS_THRU_ATTRS[key])[self.key] = value
        return super().__setattr__(key, value)

    @property
    def spatial_neighbors(self):
        """Spatial Neighbors are those that are connected to this event via space-like edges

        Returns:
            List[Event], the left and right neighbors
        """
        return [self.left, self.right]

    @property
    def temporal_neighbors(self):
        """Temporal neighbors are those that are connected to this event via time-like edges

        Returns:
            List[Event], the past and future neighbors
        """
        return self.past + self.future

    @property
    def neighbors(self):
        """All neighbors, events connected to this event via any kind of edge

        Returns:
            List[Event], all neighbor events
        """
        return self.spatial_neighbors + self.temporal_neighbors

    @property
    def is_gluing_point(self):
        """Boolean variable for determining gluing points

        Returns:
            bool, True if this event represents a gluing point, False otherwise.
        """
        return isinstance(self.key, GluingPoint)


def event_key(e: typing.Union[Event, int]) -> int:
    """Small utility function for coercing Event instances to their SpaceTime keys

    Args:
        e:
            Event or int, the event to coerce into a key (if necessary)

    Returns:
        int, the coerced event key
    """
    return e.key if isinstance(e, Event) else e


def events(space_time, keys: typing.Union[int, typing.Iterable[int]]) -> typing.Union[Event, typing.List[Event]]:
    """Helper function for creating multiple Event instances from an iterable
    of SpaceTime keys

    Args:
        space_time:
            SpaceTime, the spacetime from which events will be produced
        keys:
            Iterable[int], a collection of SpaceTime keys from which to create Events

    Returns:
        List[Event], a list of Events corresponding to the order of the given iterable of keys
    """
    if isinstance(space_time, Iterable):  # TODO more thorough check in case we make spacetime iterable..
        return zip(*[events(st, keys) for st in space_time])
    if isinstance(keys, Iterable):
        return [Event(space_time=space_time, event_key=k) for k in keys]
    return Event(space_time=space_time, event_key=keys)


class GluingPoint(int):
    """A Gluing Point represents a reference to an "open edge" or an event that
    does not belong to a particular spacetime. They are used for gluing spacetimes
    together, which primarily arises as a functional inverse to removing a subset of
    events from a spacetime (or 'cutting'). The terminology of cutting / gluing is
    borrowed from topological literature.

    The Gluing Point int subclass is used to passively identify gluing points
    as event keys without changing and fundamental behavior of the event key.
    """


def coerce_gluing_point(space_time, event: typing.Union[Event, typing.Iterable[Event]]):
    """Coerce event key to GluingPoints if the event does not belong to the space_time

    Args:
        space_time:
            SpaceTime, the spacetime object
        event:
            Event, the event to coerce. key will be wrapped as GluingPoint if event
            does not belong the space_time argument

    Returns:
        Event or List[Event], the coerced events
    """
    # Naive
    if isinstance(event, Iterable):
        return [coerce_gluing_point(space_time, v) for v in event]
    if event.key not in space_time.nodes:
        return Event(event.space_time, event_key=GluingPoint(event.key))
    return event
