"""Unittests for SpaceTime"""
import os
import pathlib
import tempfile
import sys

import networkx
import pytest

from cdtea import event, modifications, space_time
from cdtea.space_time import SpaceTime
from cdtea.space_time import generate_flat_spacetime

PY_VERSION = sys.version_info


def dummy_space_time(spatial_size: int = 2, temporal_size: int = 1):
    """Helper function for creating SpaceTime for testing"""
    st = generate_flat_spacetime(spatial_size, temporal_size)
    return st


class TestSpaceTime:
    """Test SpaceTime classes"""

    def test_dummy_space_time(self):
        """Coverage ftw"""
        dst = dummy_space_time()
        assert isinstance(dst, SpaceTime)
        assert len(dst.nodes) == 2

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

    SAMPLE_CONFIG_PICKLE_38 = (b'\x80\x04\x95\xc7\x02\x00\x00\x00\x00\x00\x00\x8c\x10cdtea.space_time\x94\x8c\tSpaceTime\x94\x93\x94)\x81\x94}\x94(\x8c\x06closed\x94\x88'
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

    SAMPLE_CONFIG_PICKLE_37 = (b'\x80\x03ccdtea.space_time\nSpaceTime\nq\x00)\x81q\x01}q\x02(X\x06\x00\x00\x00closedq\x03\x88X\x05\x00\x00\x00nodesq\x04cbuiltins\nset\nq\x05]q'
                               b'\x06(K\x00K\x01K\x02K\x03e\x85q\x07Rq\x08X\t\x00\x00\x00node_leftq\t}q\n(K\x00K\x01K\x01K\x00K\x02K\x03K\x03K\x02uX\n\x00\x00\x00node_rightq\x0b}'
                               b'q\x0c(K\x00K\x01K\x01K\x00K\x02K\x03K\x03K\x02uX\t\x00\x00\x00node_pastq\r}q\x0e(K\x00]q\x0f(K\x03K\x02eK\x01]q\x10(K\x02K\x03eK\x02]q\x11(K\x01K\x00'
                               b'eK\x03]q\x12(K\x00K\x01euX\x0b\x00\x00\x00node_futureq\x13}q\x14(K\x00]q\x15(K\x02K\x03eK\x01]q\x16(K\x03K\x02eK\x02]q\x17(K\x00K\x01eK\x03]q\x18(K\x01'
                               b'K\x00euX\x10\x00\x00\x00faces_containingq\x19}q\x1a(K\x00]q\x1b(cbuiltins\nfrozenset\nq\x1c]q\x1d(K\x00K\x01K\x03e\x85q\x1eRq\x1fh\x1c]q (K\x00'
                               b'K\x01K\x03e\x85q!Rq"h\x1c]q#(K\x00K\x02K\x03e\x85q$Rq%h\x1c]q&(K\x00K\x02'
                               b"K\x03e\x85q'Rq(h\x1c]q)(K\x00K\x01K\x02e\x85q*Rq+h\x1c]q,(K\x00K\x01K\x02"
                               b'e\x85q-Rq.eK\x01]q/(h\x1c]q0(K\x00K\x01K\x02e\x85q1Rq2h\x1c]q3(K\x00K\x01K\x02e\x85q4Rq5h\x1c]q6(K\x01K\x02K\x03e\x85q7Rq8h\x1c]q9(K\x01K\x02K\x03e'
                               b'\x85q:Rq;h\x1c]q<(K\x00K\x01K\x03e\x85q=Rq>h\x1c]q?(K\x00K\x01K\x03e\x85q@RqAeK\x02]qB(h\x1c]qC(K\x01K\x02K\x03e\x85qDRqEh\x1c]qF(K\x01K\x02'
                               b'K\x03e\x85qGRqHh\x1c]qI(K\x00K\x01K\x02e\x85qJRqKh\x1c]qL(K\x00K\x01K\x02e\x85qMRqNh\x1c]qO(K\x00K\x02K\x03e\x85qPRqQh\x1c]qR(K\x00K\x02K\x03e\x85'
                               b'qSRqTeK\x03]qU(h\x1c]qV(K\x00K\x02K\x03e\x85qWRqXh\x1c]qY(K\x00K\x02K\x03e\x85qZRq[h\x1c]q\\(K\x00K\x01K\x03e\x85q]Rq^h\x1c]q_(K\x00K\x01K\x03e\x85q'
                               b'`Rqah\x1c]qb(K\x01K\x02K\x03e\x85qcRqdh\x1c]qe(K\x01K\x02K\x03e\x85qfRqgeuX\x05\x00\x00\x00facesqhh\x05]qi(hEh\x1fhXh2e\x85qjRqkX\x0c\x00\x00\x00fa'
                               b'ce_dilatonql}qm(h\x1fJ\xff\xff\xff\xffh2J\xff\xff\xff\xffhEJ\xff\xff\xff\xffhXJ\xff\xff\xff\xffuX\x06\x00\x00\x00face_xqn}qo(h\x1f]qp(h(h\x1c]qq('
                               b'K\x01K\x02K\x03e\x85qrRqseh2]qt(h;h\x1c]qu(K\x00K\x02K\x03e\x85qvRqwehE]qx(hNh\x1c]qy(K\x00K\x01K\x03e\x85qzRq{ehX]q|(hah\x1c]q}(K\x00K\x01K\x02e\x85'
                               b'q~Rq\x7feuX\x06\x00\x00\x00face_tq\x80}q\x81(h\x1fh.h2hAhEhThXhguX\x0f\x00\x00\x00dead_referencesq\x82h\x05]q\x83\x85q\x84Rq\x85ub.')

    def _sample_pickle(self):
        if PY_VERSION.major != 3 or PY_VERSION.minor not in (7, 8):
            raise NotImplementedError('Unsupported Python Version: {}. Supported options 3.7, 3.8'.format(str(PY_VERSION)))
        return {
            (3, 8): self.SAMPLE_CONFIG_PICKLE_38,
            (3, 7): self.SAMPLE_CONFIG_PICKLE_37,
        }[(PY_VERSION.major, PY_VERSION.minor)]

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
        assert st_s == self._sample_pickle()

        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / 'test_to_pickle.pkl'
            st.to_pickle(path=path)
            assert os.path.exists(path.as_posix())  # check file written out

            with open(path.as_posix(), 'rb') as fid:
                content = fid.read()
                assert content == self._sample_pickle()

    def test_from_pickle(self):
        """Test creation of SpaceTime from pickle"""
        st = dummy_space_time(2, 2)
        st_loaded = SpaceTime.from_pickle(data=self._sample_pickle())
        assert isinstance(st_loaded, SpaceTime)
        assert st_loaded == st

        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / 'test_to_pickle.pkl'
            with open(path.as_posix(), 'wb') as fid:
                fid.write(self._sample_pickle())
            st_loaded = SpaceTime.from_pickle(path=path)
            assert isinstance(st_loaded, SpaceTime)
            assert st_loaded == st

    def test_to_networkx(self):
        """Test conversion to networkx"""
        st = dummy_space_time(2, 2)
        G = st.to_networkx()
        assert isinstance(G, networkx.Graph)
