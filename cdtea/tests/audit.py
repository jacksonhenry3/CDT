"""Various tools for auditing SpaceTime instance internals
This module exists within the tests subpackage since it is not part of the general API
but rather a set of useful tools for inspecting SpaceTime instance attributes for testing
and debugging while developing.
"""
import collections
import itertools

import pandas

from cdtea import event
from cdtea.space_time import SpaceTime


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


def find_gluing_point_references(st: SpaceTime):
    gp_nodes = []
    gp_refs = []
    for n in st.ordered_nodes:
        if isinstance(n, event.GluingPoint):
            gp_nodes.append(n)
        if isinstance(st.node_left[n], event.GluingPoint):
            gp_refs.append((n, 'left', st.node_left[n]))
        if isinstance(st.node_right[n], event.GluingPoint):
            gp_refs.append((n, 'right', st.node_right[n]))
        for f in st.node_future[n]:
            if isinstance(f, event.GluingPoint):
                gp_refs.append((n, 'future', f))
        for p in st.node_past[n]:
            if isinstance(p, event.GluingPoint):
                gp_refs.append((n, 'past', p))
    return gp_nodes, gp_refs


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



