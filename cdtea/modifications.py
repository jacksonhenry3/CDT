"""
This module contains functions that modify a spacetime.
"""
import cdtea.event as event


def move(st, node, future, past):
    """
    A move should add one node and 2 faces. we can pop all the structures to be modified out of the dicts and then push
    them back in once they've been modified. This mean we need to know what could get modfified in any given move.
    """

    # remove the sub_space that is going to be modified
    sub_space = st.pop([node])
    future_s = event.Event(sub_space, future)  # Need these two because they have been "popped" out of the original spacetime
    past_s = event.Event(sub_space, past)

    # increment the total node counter
    new_node_num = max(st.nodes.union(sub_space.nodes)) + 1
    sub_space.add_node(new_node_num)

    # create a node object for easy manipulation. This also automatically adds the node to the sub_space
    new_s = event.Event(sub_space, new_node_num)
    node_s = event.Event(sub_space, node)
    left_s = event.Event(sub_space, node_s.left)
    left = node_s.left
    right = node_s.right

    # spatial changes
    event.connect_spatial(new_s, node_s)  # new_s.right = node_s and node_s.left = new_s
    event.connect_spatial(left_s, new_s)  # new_s.left = left_s and left_s.right = new_s

    # future changes
    # TODO examine algorithm concept of connection vs Spacetime (e.g. after popping a node out, what does asking for "left" mean?)
    new_future_set = {future_s}
    f = future_s.left

    while f in node_s.future and not f.is_gluing_point:
        new_future_set.add(f)
        sub_space.node_future[node.key].remove(f.key)  # TODO cleanup the event key coercion by figuring out workaround for node.future.remove()
        sub_space.node_past[f.key].remove(node.key)
        f = f.left
    event.connect_temporal(new_s, future=new_future_set)
    old_future_set = node_s.future.difference(new_future_set).union({future_s})
    event.connect_temporal(node_s, future=old_future_set)
    # sub_space.node_past[future].append(new_node)

    # past changes
    new_past_set = {past_s}
    p = past_s.left
    while p in node_s.past:
        new_past_set.add(p)
        sub_space.node_past[node_s.key].remove(p.key)
        sub_space.node_future[p.key].remove(node_s.key)
        p = p.left
    event.connect_temporal(new_s, past=new_past_set)
    old_past_set = node_s.past.difference(new_past_set).union({past_s})
    event.connect_temporal(node_s, past=old_past_set)
    # sub_space.node_future[past].append(new_node)

    # face changes
    # remove old faces
    sub_space.faces = []

    n = future_s
    leftmost_future = n
    while n.left in new_s.future:
        v1 = n
        n = n.left
        leftmost_future = n
        new_face = frozenset([v1.key, n.key, new_s.key])
        sub_space.faces.append(new_face)
        sub_space.face_dilaton[new_face] = -1
    n = past_s
    leftmost_past = n
    while n.left in new_s.past:
        v1 = n
        n = n.left
        leftmost_past = n
        new_face = frozenset([v1.key, n.key, new_s.key])
        sub_space.faces.append(new_face)
        sub_space.face_dilaton[new_face] = 100

    n = future_s
    rightmost_future = n
    while n.right in node_s.future:
        v1 = n
        n = n.right
        rightmost_future = n
        new_face = frozenset([v1.key, n.key, node_s.key])
        sub_space.faces.append(new_face)
        sub_space.face_dilaton[new_face] = -1
    n = past_s
    rightmost_past = n
    while n.right in node_s.past:
        v1 = n
        n = n.right
        rightmost_past = n
        new_face = frozenset([v1.key, n.key, node_s.key])
        sub_space.faces.append(new_face)
        sub_space.face_dilaton[new_face] = 100

    righmost_future = future_s

    sub_space.faces.append(frozenset({node_s.key, new_s.key, future_s.key}))
    sub_space.face_dilaton[frozenset({node_s.key, new_s.key, future_s.key})] = 1
    sub_space.faces.append(frozenset({node_s.key, new_s.key, past_s.key}))
    sub_space.face_dilaton[frozenset({node_s.key, new_s.key, past_s.key})] = -1

    sub_space.faces.append(frozenset({node_s.key, right.key, rightmost_future.key}))
    sub_space.face_dilaton[frozenset({node_s.key, right.key, rightmost_future.key})] = 1
    sub_space.faces.append(frozenset({node_s.key, right.key, rightmost_past.key}))
    sub_space.face_dilaton[frozenset({node_s.key, right.key, rightmost_past.key})] = -1

    sub_space.faces.append(frozenset({left.key, new_s.key, leftmost_future.key}))
    sub_space.face_dilaton[frozenset({left.key, new_s.key, leftmost_future.key})] = 1
    sub_space.faces.append(frozenset({left.key, new_s.key, leftmost_past.key}))
    sub_space.face_dilaton[frozenset({left.key, new_s.key, leftmost_past.key})] = -1

    event.set_faces(new_s, [])
    event.set_faces(node_s, [])
    st.push(sub_space)


def imove(st, node):
    """ merge two spatially adjacent nodes, always merges in one direction?"""
    left = node.left
    sub_space = st.pop([node, left])

    left_s = event.Event(sub_space, left.key)
    node_s = event.Event(sub_space, node.key)

    new_future = set(left_s.future).union(node_s.future)
    new_past = set(left_s.past).union(node_s.past)
    new_left = left_s.left

    event.connect_spatial(new_left, node_s)
    event.connect_temporal(node_s, past=new_past, future=new_future)
    event.connect_temporal(left_s, past=set(), future=set())

    sub_space.remove_node(left_s)
    faces = sub_space.get_faces_containing(left.key)

    sub_space.faces = [x for x in sub_space.faces if x not in faces]
    for face in faces:
        new_face = []
        if node.key not in face:
            for n in face:
                if n == left.key:
                    n = node.key
                new_face.append(n)
            sub_space.faces.append(frozenset(new_face))
            sub_space.face_dilaton[frozenset(new_face)] = -1

    st.push(sub_space)
