"""This module defines properties related to nodes in spacetime as well as their manipulation. Most
non-trivial operations are reserved for the SpaceTime object, and the Node class is largely a syntactic
sugar for code readability
"""

import typing
from collections import Iterable


class PassThruAttr:
    """Constants class for pass thru attributes"""
    Left = 'left'
    Right = 'right'
    Past = 'past'
    Future = 'future'
    Faces = 'faces'


PASS_THRU_ATTR_MAP = {
    # Mapping of attribute name in Node object and corresponding lookup-dict in SpaceTime object
    # NOTE: this depends on implementation details of SpaceTime class, and should be updated in tandem
    PassThruAttr.Left: 'node_left',
    PassThruAttr.Right: 'node_right',
    PassThruAttr.Past: 'node_past',
    PassThruAttr.Future: 'node_future',
    PassThruAttr.Faces: 'faces_containing'
}
EVENT_RETURNING_ATTRS = ('left', 'right', 'past', 'future')
EDGE_CONSISTENCY_ATTR_DUALS = [
    # Mapping of attributes that define edge consistency relationships, which
    # may also be viewed as parity and time-reversal duals
    (PassThruAttr.Left, PassThruAttr.Right),
    (PassThruAttr.Past, PassThruAttr.Future),
]
EDGE_CONSISTENCY_ATTR_DUALS_DICT = dict(EDGE_CONSISTENCY_ATTR_DUALS + [(v, k) for k, v in EDGE_CONSISTENCY_ATTR_DUALS])


class Event:
    """A light-weight representation of a node in a SpaceTime. Since the SpaceTime contains
    lookup-dicts of all relevant node-edge relationships, the Node class serves as a syntactic
    sugar for passing between a particular node identifier and various feature lookups in the
    SpaceTime object.
    """

    def __init__(self, space_time, event_key):
        """Create an Event instance

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
            raise ValueError('Event Key {} not defined in spacetime: {}'.format(event_key, space_time))
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

    def _get_pass_thru_attr_(self, key):
        """Helper private method for looking up pass-thru attributes.For these attributes only,
        the call will be redirected to the underlying SpaceTime object from which the key originates

        Args:
            key:
                str, the name of the attribute to get

        Returns:
            Event, List[Event], or List[frozenset] depending on whether a single neighbor,
            multiple neighbors, or faces are requested
        """
        if key in PASS_THRU_ATTR_MAP:
            value = getattr(self.space_time, PASS_THRU_ATTR_MAP[key])[self.key]
            if key in EVENT_RETURNING_ATTRS:
                if isinstance(value, Iterable):
                    return [v if v is None else Event(space_time=self.space_time, event_key=v) for v in value]
                return value if value is None else Event(space_time=self.space_time, event_key=value)
            return value

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
        return 'Event(ST{:d}, {:d})'.format(len(self.space_time.nodes), -1 if self.key is None else self.key)

    @property
    def left(self):
        """Pass-thru accessor for left neighbor

        Returns:
            Event, the left neighbor
        """
        return self._get_pass_thru_attr_(PassThruAttr.Left)

    @property
    def right(self):
        """Pass-thru accessor for right neighbor

        Returns:
            Event, the right neighbor
        """
        return self._get_pass_thru_attr_(PassThruAttr.Right)

    @property
    def past(self):
        """Pass-thru accessor for past neighbors

        Returns:
            List[Event], the past neighbors
        """
        return self._get_pass_thru_attr_(PassThruAttr.Past)

    @property
    def future(self):
        """Pass-thru accessor for future neighbors

        Returns:
            List[Event], the future neighbors
        """
        return self._get_pass_thru_attr_(PassThruAttr.Future)

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


def events(space_time, keys: typing.Union[int, typing.Iterable[int]] = None) -> typing.Union[Event, typing.List[Event]]:
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
        return list(zip(*[events(st, keys) for st in space_time]))
    if keys is None:
        keys = space_time.nodes
    if isinstance(keys, Iterable):
        return [Event(space_time=space_time, event_key=k) for k in keys]
    return Event(space_time=space_time, event_key=keys)


def connect(self, key, value):
    """Override the behavior of attribute setting ONLY for the case of pass-thru attributes,
    which are defined above in PASS_THRU_ATTRIBUTES. for these attributes only, the setattr
    call will be redirected to the underlying SpaceTime object from which the key originates

    Args:
        key:
            str, the name of the attribute to set
        value:
            Any, if an Event instance and key is a pass-thru attr, value will be coerced to int before
            assignment to corresponding SpaceTime attribute lookup dict

    Notes:
        Edge Consistency:
            The below code ensures that both ends of edges are maintained in a way that
            preserves the following consistency relations between events A and B:

                (1) A.right = B    <==>  A = B.left
                (2) A.left = B     <==>  A = B.right
                (3) B in A.past    <==>  A in B.future
                (4) B in A.future  <==>  A in B.past

            In order to maintain relations (3) and (4), the original value of the attribute
            assigned to the given key must be tracked, so as to know which event to update
            after the new attribute assignment.
    """
    if key not in PASS_THRU_ATTR_MAP:
        return super().__setattr__(key, value)

    # Assign new value
    value_key = [event_key(v) for v in value] if isinstance(value, Iterable) else event_key(value)
    original_value = getattr(self, key)
    getattr(self.space_time, PASS_THRU_ATTR_MAP[key])[self.key] = value_key

    if original_value is None or original_value == []:
        # Short-circuit if the original value is None (this corresponds to a empty-reference)
        return

    if key not in EDGE_CONSISTENCY_ATTR_DUALS:
        # TODO define behavior for faces and face consistency
        return

    # Curate remaining values for edge-consistency
    if isinstance(value, Iterable):
        # Update the edge-consistency dual-attribute of the newly assigned event
        new_events = [n for n in value if n not in original_value]
        for n in new_events:
            if self.key not in getattr(n.space_time, PASS_THRU_ATTR_MAP[EDGE_CONSISTENCY_ATTR_DUALS[key]])[n.key]:
                getattr(n.space_time, PASS_THRU_ATTR_MAP[EDGE_CONSISTENCY_ATTR_DUALS[key]])[n.key].append(self.key)

        # Update the edge-consistency dual-attribute of the replaced event
        # TODO must decide about replaced edge behavior
        # replaced_events = [n for n in original_value if n not in value]
        # for r in replaced_events:
        #     if self.key in getattr(r.space_time, PASS_THRU_ATTRS[EDGE_CONSISTENCY_ATTR_DUALS[key]])[r.key]:
        #         getattr(r.space_time, PASS_THRU_ATTRS[EDGE_CONSISTENCY_ATTR_DUALS[key]])[r.key].remove(self.key)
    else:
        # Update the edge-consistency dual-attribute of the newly assigned event
        if getattr(value, EDGE_CONSISTENCY_ATTR_DUALS[key]) != self:
            setattr(value, EDGE_CONSISTENCY_ATTR_DUALS[key], self)

        # Update the edge-consistency dual-attribute of the replaced event
        # TODO we need to think about this behavior, the replaced event has no natural replaced attribute?
        # getattr(original_value.space_time, PASS_THRU_ATTRS[EDGE_CONSISTENCY_ATTR_DUALS[key]])[original_value.key] = None


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
