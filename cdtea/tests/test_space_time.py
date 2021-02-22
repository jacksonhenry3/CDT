"""Unittests for SpaceTime"""
import collections
import itertools
import os
import pathlib
import tempfile

import networkx
import pandas
import pytest

from cdtea import event, modifications, space_time
from cdtea.space_time import SpaceTime
from cdtea.space_time import generate_flat_spacetime


def dummy_space_time(spatial_size: int = 2, temporal_size: int = 1):
    """Helper function for creating SpaceTime for testing"""
    st = generate_flat_spacetime(spatial_size, temporal_size)
    return st


def find_duplicate_temporal_connections(st: SpaceTime):
    """Utility for finding duplicate temporal connections"""
    duplicates = []
    for n in st.ordered_nodes:
        future = st.node_future[n]
        past = st.node_past[n]
        if len(set(future)) < len(future):  # future has dups
            duplicates.append((n, 'future', future))

        if len(set(past)) < len(past):  # future has dups
            duplicates.append((n, 'past', past))

    return duplicates if duplicates != [] else None


def ranges(i):
    for a, b in itertools.groupby(enumerate(i), lambda t: t[1] - t[0]):
        b = list(b)
        yield b[0][1], b[-1][1]


# TODO move these tools somewhere real eventually
DiffSummary = collections.namedtuple('DiffSummary', 'unique_left unique_right common diffs')

def spacetime_diff(st1: SpaceTime, st2: SpaceTime, display_results: bool = False):
    """Collect difference between shared nodes in two spacetimes"""
    common_nodes = st1.nodes.intersection(st2.nodes)
    unique_nodes_1 = set(n for n in st1.nodes if n not in common_nodes)
    unique_nodes_2 = set(n for n in st2.nodes if n not in common_nodes)
    diffs = []
    for n in common_nodes:
        if st1.node_left[n] != st2.node_left[n]:
            diffs.append((n, 'left', st1.node_left[n], st2.node_left[n]))
        if st1.node_right[n] != st2.node_right[n]:
            diffs.append((n, 'right', st1.node_right[n], st2.node_right[n]))
        if st1.node_past[n] != st2.node_past[n]:
            diffs.append((n, 'past', st1.node_past[n], st2.node_past[n]))
        if st1.node_future[n] != st2.node_future[n]:
            diffs.append((n, 'future', st1.node_future[n], st2.node_future[n]))
    diffs = pandas.DataFrame([[n, t, str(l), str(r)] for n, t, l, r in diffs], columns=['Node', 'Type', 'Left', 'Right'])
    summary = DiffSummary(unique_nodes_1, unique_nodes_2, common_nodes, diffs)
    if not display_results:
        return summary
    print(format_diff(summary))


def format_diff(summary: DiffSummary) -> str:
    """Utility for formatting diff information"""
    # TODO fix indenting
    return """SpaceTime Diff Summary:

{ulc:d} Unique L Nodes: {unique_left}
{urc:d} Unique R Nodes: {unique_right}
{cc:d} Common Nodes: {common_nodes}

Diff Table:
{table}
    """.format(ulc=len(summary.unique_left),
               unique_left=str(summary.unique_left),
               urc=len(summary.unique_right),
               unique_right=str(summary.unique_right),
               cc=len(summary.common),
               common_nodes=str(list(ranges(list(sorted(summary.common))))),
               table=summary.diffs.to_string(index=False))


class TestTestingUtils:
    """Tests for the helper test functions"""

    def test_dummy_space_time(self):
        """Coverage ftw"""
        dst = dummy_space_time()
        assert isinstance(dst, SpaceTime)
        assert len(dst.nodes) == 2

    def test_find_duplicate_temp_conn(self):
        """Test duplicate connection finder"""
        valid_cdt = space_time.generate_flat_spacetime(10, 10)
        invalid_cdt = space_time.generate_flat_spacetime(10, 10)
        invalid_cdt.node_future[0] = [10, 19, 19]
        valid_dups = find_duplicate_temporal_connections(valid_cdt)
        assert valid_dups is None
        invalid_dups = find_duplicate_temporal_connections(invalid_cdt)
        assert invalid_dups is not None
        assert invalid_dups == [(0, 'future', [10, 19, 19])]

    def test_ranges(self):
        """Test ranges utility"""
        rs = list(ranges([0, 1, 2, 3, 4, 7, 8, 9, 11]))
        assert rs == [(0, 4), (7, 9), (11, 11)]

    def test_diff(self):
        """Test diff tool"""
        cdt1 = space_time.generate_flat_spacetime(3, 3)
        cdt2 = space_time.generate_flat_spacetime(3, 4)
        diff = spacetime_diff(cdt1, cdt2)
        assert isinstance(diff, DiffSummary)

    def test_diff_summary(self):
        """Test diff tool summary"""
        cdt1 = space_time.generate_flat_spacetime(3, 3)
        cdt2 = space_time.generate_flat_spacetime(3, 4)
        diff = spacetime_diff(cdt1, cdt2)
        summary = format_diff(diff)
        assert isinstance(summary, str)


class TestSpaceTime:
    """Test SpaceTime classes"""

    def test_pop(self):
        dst = dummy_space_time(3, 3)
        e0 = event.Event(dst, 0)
        dst2 = dst.pop([e0])
        assert isinstance(dst2, SpaceTime)

    def test_push(self):
        dst = dummy_space_time(3, 3)
        e0 = event.Event(dst, 0)
        dst2 = dst.pop([e0])
        dst.push(dst2)
        # TODO add real equivalence check
        assert isinstance(dst, SpaceTime)

    def test_equality(self):
        """Test equality"""
        dst = dummy_space_time(3, 3)
        dst_2 = dummy_space_time(3, 3)
        assert dst == dst_2

        e4 = event.Event(dst, 4)
        sub_dst = dst.pop([e4])
        assert dst != dst_2

    def test_pop_push_unique(self):
        """Test for temporal connection uniqueness, based on Jackson's repro 2021-02-21"""
        st = space_time.generate_flat_spacetime(10, 10)
        node = event.Event(st, 13)
        st.push(st.pop([node]))
        dups = find_duplicate_temporal_connections(st)
        assert dups is None

    def test_push_pop_identity(self):
        """Test that push * pop == identity"""
        base  = space_time.generate_flat_spacetime(10, 10) # to compare against
        st = space_time.generate_flat_spacetime(10, 10)
        assert base == st
        node = event.Event(st, 13)
        st.push(st.pop([node]))
        assert base == st


class TestSpaceTimeSerialize:
    """Serialization tests for spacetime class"""

    SAMPLE_CONFIG_DICT = {'closed': True, 'dead_references': set(),
                          'face_dilation': {frozenset({0, 1, 3}): -1, frozenset({0, 1, 2}): -1, frozenset({1, 2, 3}): -1, frozenset({0, 2, 3}): -1},
                          'face_t': {frozenset({0, 1, 3}): frozenset({0, 1, 2}), frozenset({0, 1, 2}): frozenset({0, 1, 3}), frozenset({1, 2, 3}): frozenset({0, 2, 3}),
                                     frozenset({0, 2, 3}): frozenset({1, 2, 3})},
                          'face_x': {frozenset({0, 1, 3}): [frozenset({0, 2, 3}), frozenset({1, 2, 3})], frozenset({0, 1, 2}): [frozenset({1, 2, 3}), frozenset({0, 2, 3})],
                                     frozenset({1, 2, 3}): [frozenset({0, 1, 2}), frozenset({0, 1, 3})], frozenset({0, 2, 3}): [frozenset({0, 1, 3}), frozenset({0, 1, 2})]},
                          'faces': {frozenset({1, 2, 3}), frozenset({0, 1, 3}), frozenset({0, 2, 3}), frozenset({0, 1, 2})},
                          'faces_containing': {
                              0: [frozenset({0, 1, 3}), frozenset({0, 1, 3}), frozenset({0, 2, 3}), frozenset({0, 2, 3}), frozenset({0, 1, 2}), frozenset({0, 1, 2})],
                              1: [frozenset({0, 1, 2}), frozenset({0, 1, 2}), frozenset({1, 2, 3}), frozenset({1, 2, 3}), frozenset({0, 1, 3}), frozenset({0, 1, 3})],
                              2: [frozenset({1, 2, 3}), frozenset({1, 2, 3}), frozenset({0, 1, 2}), frozenset({0, 1, 2}), frozenset({0, 2, 3}), frozenset({0, 2, 3})],
                              3: [frozenset({0, 2, 3}), frozenset({0, 2, 3}), frozenset({0, 1, 3}), frozenset({0, 1, 3}), frozenset({1, 2, 3}), frozenset({1, 2, 3})]},
                          'node_future': {0: [2, 3], 1: [3, 2], 2: [0, 1], 3: [1, 0]},
                          'node_left': {0: 1, 1: 0, 2: 3, 3: 2},
                          'node_past': {0: [3, 2], 1: [2, 3], 2: [1, 0], 3: [0, 1]},
                          'node_right': {0: 1, 1: 0, 2: 3, 3: 2},
                          'nodes': {0, 1, 2, 3}}

    SAMPLE_CONFIG_PICKLE = (b'\x80\x04\x95\xc7\x02\x00\x00\x00\x00\x00\x00\x8c\x10cdtea.space_time\x94\x8c\tSpaceTime\x94\x93\x94)\x81\x94}\x94(\x8c\x06closed\x94\x88'
                            b'\x8c\x05nodes\x94\x8f\x94(K\x00K\x01K\x02K\x03\x90\x8c\tnode_left\x94}\x94(K\x00K\x01K\x01K\x00K\x02K\x03K\x03K\x02u\x8c\nnode_right\x94}\x94(K\x00K\x01'
                            b'K\x01K\x00K\x02K\x03K\x03K\x02u\x8c\tnode_past\x94}\x94(K\x00]\x94(K\x03K\x02eK\x01]\x94(K\x02K\x03eK\x02]\x94(K\x01K\x00eK\x03]\x94(K\x00K\x01e'
                            b'u\x8c\x0bnode_future\x94}\x94(K\x00]\x94(K\x02K\x03eK\x01]\x94(K\x03K\x02eK\x02]\x94(K\x00K\x01eK\x03]\x94(K\x01K\x00eu\x8c\x10faces_containin'
                            b'g\x94}\x94(K\x00]\x94((K\x00K\x01K\x03\x91\x94(K\x00K\x01K\x03\x91\x94(K\x00K\x02K\x03\x91\x94(K\x00K\x02K\x03\x91\x94(K\x00K\x01K\x02\x91\x94('
                            b'K\x00K\x01K\x02\x91\x94eK\x01]\x94((K\x00K\x01K\x02\x91\x94(K\x00K\x01K\x02\x91\x94(K\x01K\x02K\x03\x91\x94(K\x01K\x02K\x03\x91\x94(K\x00K\x01K'
                            b'\x03\x91\x94(K\x00K\x01K\x03\x91\x94eK\x02]\x94((K\x01K\x02K\x03\x91\x94(K\x01K\x02K\x03\x91\x94(K\x00K\x01K\x02\x91\x94(K\x00K\x01K\x02\x91\x94(K'
                            b'\x00K\x02K\x03\x91\x94(K\x00K\x02K\x03\x91\x94eK\x03]\x94((K\x00K\x02K\x03\x91\x94(K\x00K\x02K\x03\x91\x94(K\x00K\x01K\x03\x91\x94(K\x00K\x01K\x03'
                            b'\x91\x94(K\x01K\x02K\x03\x91\x94(K\x01K\x02K\x03\x91\x94eu\x8c\x05faces\x94\x8f\x94(h)h\x1bh0h"\x90\x8c\x0cface_dilaton\x94}\x94(h\x1bJ\xff'
                            b'\xff\xff\xffh"J\xff\xff\xff\xffh)J\xff\xff\xff\xffh0J\xff\xff\xff\xffu\x8c\x06face_x\x94}\x94(h\x1b]\x94(h\x1e(K\x01K\x02K\x03\x91\x94eh"]\x94(h'
                            b'%(K\x00K\x02K\x03\x91\x94eh)]\x94(h,(K\x00K\x01K\x03\x91\x94eh0]\x94(h3(K\x00K\x01K\x02\x91\x94eu\x8c\x06face_t\x94}\x94(h\x1bh h"h\'h)h.h0h5u\x8c\x0fdead_references\x94\x8f\x94ub.')

    def test_to_dict(self):
        """Test serialization to dict"""
        st = dummy_space_time(2, 2)
        config_dict = st.to_dict()
        assert config_dict == self.SAMPLE_CONFIG_DICT

    def test_from_dict(self):
        """Load SpaceTime from dictionary"""
        st_loaded = SpaceTime.from_dict(config_dict=self.SAMPLE_CONFIG_DICT)
        st = dummy_space_time(2, 2)
        assert isinstance(st_loaded, SpaceTime)
        assert st_loaded == st

        # Test incomplete dict raises error
        incomplete_dict = self.SAMPLE_CONFIG_DICT.copy()
        incomplete_dict.pop('nodes')
        with pytest.raises(space_time.SerializationError):
            SpaceTime.from_dict(incomplete_dict)

    def test_to_pickle(self):
        """Test conversion of SpaceTime to pickle data"""
        st = dummy_space_time(2, 2)
        st_s = st.to_pickle()
        assert st_s == self.SAMPLE_CONFIG_PICKLE

        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / 'test_to_pickle.pkl'
            st.to_pickle(path=path)
            assert os.path.exists(path.as_posix())  # check file written out

            with open(path.as_posix(), 'rb') as fid:
                content = fid.read()
                assert content == self.SAMPLE_CONFIG_PICKLE

    def test_from_pickle(self):
        """Test creation of SpaceTime from pickle"""
        st = dummy_space_time(2, 2)
        st_loaded = SpaceTime.from_pickle(data=self.SAMPLE_CONFIG_PICKLE)
        assert isinstance(st_loaded, SpaceTime)
        assert st_loaded == st

        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / 'test_to_pickle.pkl'
            with open(path.as_posix(), 'wb') as fid:
                fid.write(self.SAMPLE_CONFIG_PICKLE)
            st_loaded = SpaceTime.from_pickle(path=path)
            assert isinstance(st_loaded, SpaceTime)
            assert st_loaded == st

    def test_to_networkx(self):
        """Test conversion to networkx"""
        st = dummy_space_time(2, 2)
        G = st.to_networkx()
        assert isinstance(G, networkx.Graph)
