"""
This module contains functions that modify a spacetime.
"""
import cdtea.event as event
import cdtea.face as face


def increase(st, node, future, past):
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
    sub_space.add_key(new_node_num)

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

    # remove old faces from faces_containing
    for face in sub_space.faces:
        if node_s.key in face:
            for n in face:
                sub_space.faces_containing[n].remove(face)

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

    for face in sub_space.faces:
        for n in face:
            sub_space.faces_containing[n].add(face)

    event.set_faces(new_s, [])
    event.set_faces(node_s, [])
    st.push(sub_space)


def decrease(st, node):
    """ merge two spatially adjacent nodes, always merges in one direction."""
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

    faces = set(sub_space.faces_containing[left_s.key])

    # remove faces that involve the old node

    for face in sub_space.faces:

        if left_s.key in face:
            for n in face:
                sub_space.faces_containing[n].remove(face)
    sub_space.remove_key(left_s.key)
    face_map = {f: f for f in st.faces | set(sub_space.faces)}
    sub_space.faces = {x for x in sub_space.faces if x not in faces}

    new_faces = []
    old_faces = []

    for face in faces:
        new_face = []
        if node.key not in face:
            for n in face:
                if n == left_s.key:
                    n = node.key
                new_face.append(n)

            f = frozenset(new_face)
            new_faces.append(frozenset(new_face))
            old_faces.append(face)
            face_map[face] = f

    for i, new_face in enumerate(new_faces):
        old_face = old_faces[i]

        sub_space.faces.add(new_face)

        sub_space.face_left[new_face] = face_map[sub_space.face_left[old_face]]
        sub_space.face_right[new_face] = face_map[sub_space.face_right[old_face]]

        sub_space.face_t[new_face] = face_map[sub_space.face_t[old_face]]
        sub_space.face_type[new_face] = sub_space.face_type[old_face]
        sub_space.face_dilaton[new_face] = -1

    for face in sub_space.faces:
        for n in face:
            sub_space.faces_containing[n].add(face)

    st.push(sub_space)


def new_decrease(st, node):
    """merges node.left in to node"""
    # cut out the sub_space that will be effected by the move
    left = node.left
    sub_space = st.pop([node, left])

    # identify the nodes that will be merged in the sub_space
    left_s = event.Event(sub_space, left.key)
    node_s = event.Event(sub_space, node.key)

    # ------- modify the nodes -------

    # the new neighbors of the merged node
    new_future = set(left_s.future).union(node_s.future)
    new_past = set(left_s.past).union(node_s.past)
    new_left = left_s.left

    # connect new neighbors to node and remove connections from left
    event.connect_spatial(new_left, node_s)
    event.connect_temporal(node_s, past=new_past, future=new_future)
    event.connect_temporal(left_s, past=set(), future=set())

    # ------- modify the faces -------
    # only two faces are "removed" while some others need to be relabeled.

    faces_containing_left = []
    faces_for_deletion = []
    for f in face.faces(sub_space):
        if left_s.key in f.nodes:

            if node.key in f.nodes:
                faces_for_deletion.append(f)
            else:
                faces_containing_left.append(f)

    for f in face.faces(sub_space, faces_containing_left):

        new_f_nodes = set(f.nodes)
        new_f_nodes.remove(left_s.key)
        new_f_nodes.add(node_s.key)
        new_f_nodes = frozenset(new_f_nodes)

        sub_space.face_nodes[f.key] = new_f_nodes


    # connect the newly adjacent faces and remove the old face that used to be between them
    # print(faces_for_deletion)
    for f in face.faces(sub_space, faces_for_deletion):
        face.connect_spatial(f.left, f.right)
        sub_space.remove_face(f.key)

    sub_space.remove_key(left_s.key)

    # push the modified sub_space back in to the space_time
    st.push(sub_space)
