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

DiffSummary = collections.namedtuple('DiffSummary', 'unique_left unique_right common diffs')
DegreeSummary = collections.namedtuple('DegreeSummary', 'degree missing')


class AuditError(ValueError):
    """Error subclass for audit-related errors"""


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


def node_diff(st1: SpaceTime, st2: SpaceTime, display_results: bool = False):
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


def face_diff(st1: SpaceTime, st2: SpaceTime, display_results: bool = False):
    """Collect difference between shared faces in two spacetimes"""
    common_faces = st1.faces.intersection(st2.faces)
    unique_faces_1 = st1.faces.difference(common_faces) # set(n for n in st1.faces if n not in common_faces)
    unique_faces_2 = st2.faces.difference(common_faces) # set(n for n in st2.faces if n not in common_faces)
    diffs = []
    for n in common_faces:
        if st1.face_x[n] != st2.face_x[n]:
            diffs.append((n, 'x', st1.face_x[n], st2.face_x[n]))
        if st1.face_t[n] != st2.face_t[n]:
            diffs.append((n, 't', st1.face_t[n], st2.face_t[n]))
    diffs = pandas.DataFrame([[n, t, str(l), str(r)] for n, t, l, r in diffs], columns=['Node', 'Type', 'Left', 'Right'])
    summary = DiffSummary(unique_faces_1, unique_faces_2, common_faces, diffs)
    if not display_results:
        return summary
    print(format_diff(summary, diff_type='face'))


def format_diff(summary: DiffSummary, diff_type: str = 'node') -> str:
    """Utility for formatting diff information"""
    if diff_type == 'node':
        item_label = 'Nodes'
    elif diff_type == 'face':
        item_label = 'Faces'
    else:
        raise AuditError('Unknown diff format type: {}, options are: node, face'.format(diff_type))
    # TODO fix indenting
    return """SpaceTime Diff Summary:

{ulc:d} Unique L {label}: {unique_left}
{urc:d} Unique R {label}: {unique_right}
{cc:d} Common {label}: {common}

Diff Table:
{table}
    """.format(label=item_label,
               ulc=len(summary.unique_left),
               unique_left=str(summary.unique_left),
               urc=len(summary.unique_right),
               unique_right=str(summary.unique_right),
               cc=len(summary.common),
               common=str(list(ranges(list(sorted(summary.common))))) if diff_type == 'node' else str(summary.common),
               table='None' if summary.diffs.empty else summary.diffs.to_string(index=False))


def degree(st: SpaceTime) -> DegreeSummary:
    nodes_by_degree = collections.defaultdict(list)
    nodes_missing = []
    for n in st.ordered_nodes:
        left = st.node_left[n]
        right = st.node_right[n]
        past = st.node_past[n]
        future = st.node_future[n]

        if not isinstance(left, int):
            nodes_missing.append((n, 'left', str(left)))
        if not isinstance(right, int):
            nodes_missing.append((n, 'right', str(right)))
        if not isinstance(past, set) or all(not isinstance(p, int) for p in past):
            nodes_missing.append((n, 'past', str(past)))
        if not isinstance(future, set) or all(not isinstance(f, int) for f in future):
            nodes_missing.append((n, 'future', str(future)))

        d = len([x for x in ([left, right] + ([past] if not isinstance(past, set) else list(past)) + ([future] if not isinstance(future, set) else list(future))) if isinstance(x, int)])
        nodes_by_degree[d].append(n)
    nodes_missing = pandas.DataFrame(data=nodes_missing, columns=['Node', 'Type', 'Value'])
    return DegreeSummary(degree=nodes_by_degree, missing=nodes_missing)
