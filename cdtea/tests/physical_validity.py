# physical constraints. Eventually we should have a set of these that replace assert isinstance(dst, SpaceTime) with a more physical check
from cdtea.event import events
from cdtea.space_time import SpaceTime


def is_physically_valid(st: SpaceTime):
    """
    Run all physical validity tests on st
    """

    #these can be uncommneted once this has been merged with the feature/faces_containing_fix branch
    # test_faces_containing_size(st)
    # test_accuracy_of_faces_containing(st)
    test_total_neighbors(st)
    test_future(st)
    test_past(st)
    test_right(st)
    test_right(st)
    test_faces_refrence_valid_nodes(st)


def test_faces_containing_size(st: SpaceTime):
    """
    in a physical spacetime a node must be contained in at least 4 faces. Otherwise it is missing a space or time connection.
    """
    # This is actually only true if the space_time is large enough. WHen it is small enough one node may be two different neighors reducing the total number of faces containing.
    for n in st.faces_containing:
        assert len(st.faces_containing[n]) > 4


def test_accuracy_of_faces_containing(st: SpaceTime):
    for n in st.nodes:
        assert st.faces_containing[n] == {f for f in st.faces if n in f}


def test_total_neighbors(st: SpaceTime):
    """
    in a physical spacetime a node must be contained in at least 4 other nodes. Otherwise it is missing a space or time connection.
    """
    # This is actually only true if the space_time is large enough. WHen it is small enough one node may be two different neighors reducing the total number of neighbors.
    for n in events(st):
        assert len(n.neighbors) >= 4


def test_future(st: SpaceTime):
    """
    each node must have at least one future
    """
    for n in st.nodes:
        assert len(st.node_future[n]) >= 1


def test_past(st: SpaceTime):
    """
    each node must have at least one past
    """
    for n in st.nodes:
        assert len(st.node_past[n]) >= 1


def test_right(st: SpaceTime):
    """
    each node must have exactly one right
    """
    for n in events(st):
        assert n.right.key in st.nodes


def test_right(st: SpaceTime):
    """
    each node must exactly one left
    """
    for n in events(st):
        assert n.left.key in st.nodes


def test_faces_refrence_valid_nodes(st: SpaceTime):
    """ faces must only contain nodes that are in the space_time"""
    for f in st.faces:
        for n in f:
            assert n in st.nodes
