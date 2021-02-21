from cdtea import space_time
from cdtea.visualization import plot_st


class TestPlot:
    """Test Plotting"""

    def test_plot_3d_nx(self):
        """Test Plot 3D NX"""
        st = space_time.generate_flat_spacetime(3, 3)
        plot_st.plot_3d_nx(st, render=False)
