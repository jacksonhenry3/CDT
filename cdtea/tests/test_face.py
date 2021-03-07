from cdtea import face, space_time
from cdtea.space_time import SpaceTime


class TestFace:
    """Tests for Event class"""

    def test_face_init(self):
        """Test event init from spacetime and key"""
        dst = space_time.generate_flat_spacetime(2, 2)
        f = face.Face(space_time=dst, nodes=frozenset([0, 1, 2]))
        assert isinstance(f, face.Face)
        assert id(f.space_time) == id(dst)

    def test_face_equality(self):
        """Test Event equality"""
        dst = space_time.generate_flat_spacetime(2, 2)
        e1 = face.Face(space_time=dst, nodes=frozenset([0, 1, 2]))
        e2 = face.Face(space_time=dst, nodes=frozenset([0, 1, 2]))
        assert e1 == e2

        # TODO uncomment the below test once equality defined for SpaceTime
        dst2 = space_time.generate_flat_spacetime(2, 3)
        e1_2 = face.Face(space_time=dst2, nodes=frozenset([0, 1, 2]))
        assert e1 != e1_2

    def test_face_repr(self):
        """Test event string representation"""
        dst = space_time.generate_flat_spacetime(2, 2)
        f = face.Face(space_time=dst, nodes=frozenset([0, 1, 2]))
        assert repr(f) == 'Face(ST4, {0, 1, 2})'
    #
    def test_face_pass_thru_getattr(self):
        """Test event getattr behavior for passthru attributes"""
        dst = space_time.generate_flat_spacetime(3, 3)
        face_list = [frozenset({2, 3, 5}), frozenset({1, 2, 5}), frozenset({3, 5, 6})]
        e0, e1, e2 = face.faces(dst, face_list)
        assert e0.left == e1
        assert e1.right == e0
        assert e0.temporal_neighbor == e2
        assert e0.type == 1
    #
    def test_face_safe_getattr(self):
        """Test event getattr behavior for non passthru attributes"""
        dst = space_time.generate_flat_spacetime(2, 2)
        e0 = face.Face(space_time=dst, nodes=frozenset({0,1,2}))
        assert isinstance(e0.space_time, SpaceTime)
        assert isinstance(e0.nodes, frozenset)
    #
    def test_face_hash(self):
        """Test Event Hash"""
        dst_1 = space_time.generate_flat_spacetime(2, 2)
        f0_1, *_ = face.faces(dst_1)

        dst_2 = space_time.generate_flat_spacetime(2, 2)
        f0_2, *_ = face.faces(dst_2)

        assert hash(f0_1) == hash(f0_2)

    def test_spatial_neighbors(self):
        """Test spatial neighbors"""
        dst = space_time.generate_flat_spacetime(3, 3)
        face_list = [frozenset({2, 3, 5}), frozenset({1, 2, 5}), frozenset({1, 4, 5})]
        e0, e1, e2 = face.faces(dst, face_list)
        assert e1.spatial_neighbors == {e0, e2}


    def test_neighbors(self):
        """Test neighbors"""
        dst = space_time.generate_flat_spacetime(3, 3)
        face_list = [frozenset({2, 3, 5}), frozenset({1, 2, 5}), frozenset({1, 4, 5}),frozenset({1, 2, 7})]
        e0, e1, e2, e3 = face.faces(dst, face_list)
        assert e1.neighbors == {e0, e2, e3}
