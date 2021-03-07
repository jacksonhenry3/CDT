"""Tests for simulation utilities"""
from cdtea import space_time, simulation


class TestSimulate:
    """Tests for simulation"""

    def test_simulate_no_sampling(self):
        st = space_time.generate_flat_spacetime(10, 10)
        simulation.simulate(st, iters=5)
        assert isinstance(st, space_time.SpaceTime)

    def test_simulate_with_sampling(self):
        def size(st):
            return len(st.nodes)

        sample_funcs = {'size': size}
        st = space_time.generate_flat_spacetime(10, 10)
        samples = simulation.simulate(st, iters=6, sampling_interval=2, sampling_funcs=sample_funcs)
        assert isinstance(samples, dict)
        assert set(samples.keys()) == {'size'}
        assert len(samples['size']) == 3
