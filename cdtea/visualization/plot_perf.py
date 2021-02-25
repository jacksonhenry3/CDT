"""Performance plots"""
import pandas
from plotly import graph_objects


def time_surface(timing_df: pandas.DataFrame, x: str, y: str, value: str, log_x: bool = False, log_y: bool = False, log_z: bool = False):
    # prepare dense data array
    data = timing_df[[x, y, value]].set_index([x, y])[value].unstack(y)

    # setup Figure
    fig = graph_objects.Figure(data=[graph_objects.Surface(x=data.index.values, y=data.columns, z=data.values)])
    fig.update_traces(contours_z=dict(show=True,
                                      usecolormap=True,
                                      highlightcolor="limegreen", project_z=True))

    x_label = '{}{}{}'.format('Ln[' if log_x else '', x, ']' if log_x else '')
    y_label = '{}{}{}'.format('Ln[' if log_y else '', y, ']' if log_y else '')
    z_label = '{}{}{}'.format('Ln[' if log_z else '', value, ']' if log_z else '')
    fig.update_layout(title='Performance: {} v. {} and {}'.format(z_label, x_label, y_label),
                      # autosize=False,
                      # width=500, height=500,
                      scene=dict(
                          xaxis_title=x_label,
                          yaxis_title=y_label,
                          zaxis_title=z_label),
                      margin=dict(l=65, r=50, b=65, t=90))

    fig.show()
