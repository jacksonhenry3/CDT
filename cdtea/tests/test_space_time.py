"""Unittests for SpaceTime"""
import collections
import itertools
import os
import pathlib
import tempfile
import sys

import networkx
import pandas
import pytest

from cdtea import event, moves, space_time
from cdtea.space_time import SpaceTime
from cdtea.tests import audit
from cdtea.space_time import generate_flat_spacetime

PY_VERSION = sys.version_info


class TestSpaceTime:
    """Test SpaceTime classes"""

    def test_pop(self):
        dst = space_time.generate_flat_spacetime(3, 3)
        e0 = event.Event(dst, 0)
        dst2 = dst.pop([e0])
        assert isinstance(dst2, SpaceTime)

    def test_push(self):
        dst = space_time.generate_flat_spacetime(3, 3)
        e0 = event.Event(dst, 0)
        dst2 = dst.pop([e0])
        dst.push(dst2)
        # TODO add real equivalence check
        assert isinstance(dst, SpaceTime)

    def test_equality(self):
        """Test equality"""
        dst = space_time.generate_flat_spacetime(3, 3)
        dst_2 = space_time.generate_flat_spacetime(3, 3)
        assert dst == dst_2

        e4 = event.Event(dst, 4)
        sub_dst = dst.pop([e4])
        assert dst != dst_2

    def test_pop_push_unique(self):
        """Test for temporal connection uniqueness, based on Jackson's repro 2021-02-21"""
        st = space_time.generate_flat_spacetime(10, 10)
        node = event.Event(st, 13)
        st.push(st.pop([node]))
        dups = audit.find_duplicate_temporal_connections(st)
        assert dups is None

    def test_push_pop_identity(self):
        """Test that push * pop == identity"""
        base = space_time.generate_flat_spacetime(10, 10)  # to compare against
        st = space_time.generate_flat_spacetime(10, 10)
        assert base == st
        node = event.Event(st, 13)
        st.push(st.pop([node]))
        assert base == st

    def test_push_pop_gluing_points(self):
        st = space_time.generate_flat_spacetime(10, 10)
        node = event.Event(st, 13)
        st.push(st.pop([node]))
        gp_nodes, gp_refs = audit.find_gluing_point_references(st)
        assert gp_nodes == []
        assert gp_refs == []


class TestSpaceTimeSerialize:
    """Serialization tests for spacetime class"""

    SAMPLE_CONFIG_DICT = {'closed': True, 'face_dilaton': {frozenset({0, 1, 3}): -1, frozenset({0, 1, 2}): -1, frozenset({1, 2, 3}): -1, frozenset({0, 2, 3}): -1},
                          'face_t': {frozenset({0, 1, 3}): frozenset({0, 1, 2}), frozenset({0, 1, 2}): frozenset({0, 1, 3}), frozenset({1, 2, 3}): frozenset({0, 2, 3}),
                                     frozenset({0, 2, 3}): frozenset({1, 2, 3})},
                          'face_x': {frozenset({0, 1, 3}): [frozenset({0, 2, 3}), frozenset({1, 2, 3})], frozenset({0, 1, 2}): [frozenset({1, 2, 3}), frozenset({0, 2, 3})],
                                     frozenset({1, 2, 3}): [frozenset({0, 1, 2}), frozenset({0, 1, 3})], frozenset({0, 2, 3}): [frozenset({0, 1, 3}), frozenset({0, 1, 2})]},
                          'faces': {frozenset({1, 2, 3}), frozenset({0, 1, 3}), frozenset({0, 2, 3}), frozenset({0, 1, 2})},
                          'faces_containing': {0: {frozenset({0, 1, 3}), frozenset({0, 2, 3}), frozenset({0, 1, 2})},
                                               1: {frozenset({0, 1, 2}), frozenset({1, 2, 3}), frozenset({0, 1, 3})},
                                               2: {frozenset({1, 2, 3}), frozenset({0, 1, 2}), frozenset({0, 2, 3})},
                                               3: {frozenset({0, 2, 3}), frozenset({0, 1, 3}), frozenset({1, 2, 3})}}, 'node_future': {0: {2, 3}, 1: {2, 3}, 2: {0, 1}, 3: {0, 1}},
                          'node_left': {0: 1, 1: 0, 2: 3, 3: 2}, 'node_past': {0: {2, 3}, 1: {2, 3}, 2: {0, 1}, 3: {0, 1}}, 'node_right': {0: 1, 1: 0, 2: 3, 3: 2},
                          'nodes': {0, 1, 2, 3}}

    SAMPLE_CONFIG_PICKLE_38 = (b'\x80\x04\x95\x94\x02\x00\x00\x00\x00\x00\x00\x8c\x10cdtea.space_time\x94\x8c\tSpaceTime\x94\x93\x94)\x81\x94N}\x94('
                               b'\x8c\x0e_ordered_nodes\x94N\x8c\x06closed\x94\x88\x8c\x05nodes\x94\x8f\x94(K\x00K\x01K\x02K\x03\x90\x8c\tnode_left\x94}\x94('
                               b'K\x00K\x01K\x01K\x00K\x02K\x03K\x03K\x02u\x8c\nnode_right\x94}\x94(K\x00K\x01K\x01K\x00K\x02K\x03K\x03K\x02u\x8c\tnode_past\x94}\x94('
                               b'K\x00\x8f\x94('
                               b'K\x02K\x03\x90K\x01\x8f\x94(K\x02K\x03\x90K\x02\x8f\x94(K\x00K\x01\x90K\x03\x8f\x94(K\x00K\x01\x90u\x8c\x0bnode_future\x94}\x94(K\x00\x8f\x94('
                               b'K\x02K\x03\x90K\x01\x8f\x94(K\x02K\x03\x90K\x02\x8f\x94(K\x00K\x01\x90K\x03\x8f\x94(K\x00K\x01\x90u\x8c\x10faces_containing\x94}\x94('
                               b'K\x00\x8f\x94(('
                               b'K\x00K\x01K\x03\x91\x94(K\x00K\x02K\x03\x91\x94(K\x00K\x01K\x02\x91\x94\x90K\x01\x8f\x94((K\x01K\x02K\x03\x91\x94(K\x00K\x01K\x03\x91\x94('
                               b'K\x00K\x01K\x02\x91\x94\x90K\x02\x8f\x94((K\x01K\x02K\x03\x91\x94(K\x00K\x02K\x03\x91\x94(K\x00K\x01K\x02\x91\x94\x90K\x03\x8f\x94(('
                               b'K\x01K\x02K\x03\x91\x94('
                               b'K\x00K\x01K\x03\x91\x94(K\x00K\x02K\x03\x91\x94\x90u\x8c\x05faces\x94\x8f\x94(h$h\x1ch*h"\x90\x8c\x0cface_dilaton\x94}\x94('
                               b'h\x1cJ\xff\xff\xff\xffh"J\xff\xff\xff\xffh$J\xff\xff\xff\xffh*J\xff\xff\xff\xffu\x8c\x06face_x\x94}\x94(h\x1c]\x94((K\x00K\x02K\x03\x91\x94('
                               b'K\x01K\x02K\x03\x91\x94eh"]\x94((K\x01K\x02K\x03\x91\x94(K\x00K\x02K\x03\x91\x94eh$]\x94((K\x00K\x01K\x02\x91\x94('
                               b'K\x00K\x01K\x03\x91\x94eh*]\x94(('
                               b'K\x00K\x01K\x03\x91\x94(K\x00K\x01K\x02\x91\x94eu\x8c\x06face_t\x94}\x94(h\x1c(K\x00K\x01K\x02\x91\x94h"(K\x00K\x01K\x03\x91\x94h$('
                               b'K\x00K\x02K\x03\x91\x94h*('
                               b'K\x01K\x02K\x03\x91\x94uu\x86\x94b.')

    SAMPLE_CONFIG_PICKLE_37 = (b'\x80\x03ccdtea.space_time\nSpaceTime\nq\x00)\x81q\x01N}q\x02(X\x0e\x00\x00\x00_ordered_nodesq\x03NX\x06\x00\x00\x00closedq\x04\x88X\x05\x00'
                               b'\x00\x00nodesq\x05cbuiltins\nset\nq\x06]q\x07(K\x00K\x01K\x02K\x03e\x85q\x08Rq\tX\t\x00\x00\x00node_leftq\n}q\x0b(K\x00K\x01K\x01K\x00K\x02K\x03'
                               b'K\x03K\x02uX\n\x00\x00\x00node_rightq\x0c}q\r(K\x00K\x01K\x01K\x00K\x02K\x03K\x03K\x02uX\t\x00\x00\x00node_pastq\x0e}q\x0f(K\x00h\x06]q\x10(K'
                               b'\x02K\x03e\x85q\x11Rq\x12K\x01h\x06]q\x13(K\x02K\x03e\x85q\x14Rq\x15K\x02h\x06]q\x16(K\x00K\x01e\x85q\x17Rq\x18K\x03h\x06]q\x19('
                               b'K\x00K\x01e\x85q\x1a'
                               b'Rq\x1buX\x0b\x00\x00\x00node_futureq\x1c}q\x1d(K\x00h\x06]q\x1e(K\x02K\x03e\x85q\x1fRq K\x01h\x06]q!(K\x02K\x03e\x85q"Rq#K\x02h\x06]q$(K\x00K\x01'
                               b"e\x85q%Rq&K\x03h\x06]q'(K\x00K\x01e\x85q(Rq)uX\x10\x00\x00\x00faces_contai"
                               b'ningq*}q+(K\x00]q,(cbuiltins\nfrozenset\nq-]q.(K\x00K\x01K\x03e\x85q/Rq0h-]q1(K\x00K\x01K\x03e\x85q2Rq3h-]q4(K\x00K\x02K\x03e\x85q5Rq6h-]q7(K'
                               b'\x00K\x02K\x03e\x85q8Rq9h-]q:(K\x00K\x01K\x02e\x85q;Rq<h-]q=(K\x00K\x01K\x02e\x85q>Rq?eK\x01]q@(h-]qA(K\x00K\x01K\x02e\x85qBRqCh-]qD(K\x00'
                               b'K\x01K\x02e\x85qERqFh-]qG(K\x01K\x02K\x03e\x85qHRqIh-]qJ(K\x01K\x02K\x03e\x85qKRqLh-]qM(K\x00K\x01K\x03e\x85qNRqOh-]qP(K\x00K\x01K\x03e\x85qQ'
                               b'RqReK\x02]qS(h-]qT(K\x01K\x02K\x03e\x85qURqVh-]qW(K\x01K\x02K\x03e\x85qXRqYh-]qZ(K\x00K\x01K\x02e\x85q[Rq\\h-]q](K\x00K\x01K\x02e\x85q^Rq_h-]q`('
                               b'K\x00K\x02K\x03e\x85qaRqbh-]qc(K\x00K\x02K\x03e\x85qdRqeeK\x03]qf(h-]qg(K\x00K\x02K\x03e\x85qhRqih-]qj(K\x00K\x02K\x03e\x85qkRqlh-]qm(K\x00K\x01K'
                               b'\x03e\x85qnRqoh-]qp(K\x00K\x01K\x03e\x85qqRqrh-]qs(K\x01K\x02K\x03e\x85qtRquh-]qv(K\x01K\x02K\x03e\x85qwRqxeuX\x05\x00\x00\x00facesqyh\x06]qz('
                               b'hVh0hih'
                               b'Ce\x85q{Rq|X\x0c\x00\x00\x00face_dilatonq}}q~(h0J\xff\xff\xff\xffhCJ\xff\xff\xff\xffhVJ\xff\xff\xff\xffhiJ\xff\xff\xff\xffuX\x06\x00\x00\x00fac'
                               b'e_xq\x7f}q\x80(h0]q\x81(h9h-]q\x82(K\x01K\x02K\x03e\x85q\x83Rq\x84ehC]q\x85(hLh-]q\x86(K\x00K\x02K\x03e\x85q\x87Rq\x88ehV]q\x89(h_h-]q\x8a(K'
                               b'\x00K\x01K\x03e\x85q\x8bRq\x8cehi]q\x8d(hrh-]q\x8e(K\x00K\x01K\x02e\x85q\x8fRq\x90euX\x06\x00\x00\x00face_tq\x91}q\x92('
                               b'h0h?hChRhVhehihxuu\x86q\x93b.')

    def _sample_pickle(self):
        if PY_VERSION.major != 3 or PY_VERSION.minor not in (7, 8):
            raise NotImplementedError('Unsupported Python Version: {}. Supported options 3.7, 3.8'.format(str(PY_VERSION)))
        return {(3, 8): self.SAMPLE_CONFIG_PICKLE_38, (3, 7): self.SAMPLE_CONFIG_PICKLE_37, }[(PY_VERSION.major, PY_VERSION.minor)]

    def test_to_dict(self):
        """Test serialization to dict"""
        st = space_time.generate_flat_spacetime(2, 2)
        config_dict = st.to_dict()
        assert config_dict == self.SAMPLE_CONFIG_DICT

    def test_from_dict(self):
        """Load SpaceTime from dictionary"""
        st_loaded = SpaceTime.from_dict(config_dict=self.SAMPLE_CONFIG_DICT)
        st = space_time.generate_flat_spacetime(2, 2)
        assert isinstance(st_loaded, SpaceTime)
        assert st_loaded == st

        # Test incomplete dict raises error
        incomplete_dict = self.SAMPLE_CONFIG_DICT.copy()
        incomplete_dict.pop('nodes')
        with pytest.raises(space_time.SerializationError):
            SpaceTime.from_dict(incomplete_dict)

    def test_to_pickle(self):
        """Test conversion of SpaceTime to pickle data"""
        st = space_time.generate_flat_spacetime(2, 2)
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
        st = space_time.generate_flat_spacetime(2, 2)
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
        st = space_time.generate_flat_spacetime(2, 2)
        G = st.to_networkx()
        assert isinstance(G, networkx.Graph)
