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
    layer = node.layer
    sub_space = st.pop([node])
    future_s = event.Event(sub_space, future)  # Need these two because they have been "popped" out of the original spacetime
    past_s = event.Event(sub_space, past)

    # increment the total node counter
    new_node_num = max(st.nodes.union(sub_space.nodes)) + 1
    sub_space.add_key(new_node_num, layer=layer)

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

    for f in face.faces(sub_space):
        if node_s.key in f.nodes:
            modified = [i.key for i in list(new_future_set | new_past_set | {node_s, left})]
            if all(item in modified for item in f.nodes):
                new_nodes = set(f.nodes)
                new_nodes.remove(node_s.key)
                new_nodes.add(new_s.key)

                sub_space.face_nodes[f.key] = frozenset(new_nodes)
                sub_space.faces_containing[node_s.key].remove(f.key)
                sub_space.faces_containing[new_s.key].add(f.key)

    f1r = face.Face(sub_space, (set(sub_space.faces_containing[new_s.key]) & set(sub_space.faces_containing[future_s.key])).pop())
    f1l = face.Face(sub_space, (set(sub_space.faces_containing[node_s.key]) & set(sub_space.faces_containing[future_s.key])).pop())
    f2r = face.Face(sub_space, (set(sub_space.faces_containing[new_s.key]) & set(sub_space.faces_containing[past_s.key])).pop())
    f2l = face.Face(sub_space, (set(sub_space.faces_containing[node_s.key]) & set(sub_space.faces_containing[past_s.key])).pop())

    new_face_key = max(st.faces.union(sub_space.faces)) + 1

    f_new_1 = face.Face(sub_space, sub_space.add_face(frozenset({new_s.key, node_s.key, future_s.key}), new_face_key))
    sub_space.face_type[f_new_1.key] = 0
    f_new_2 = face.Face(sub_space, sub_space.add_face(frozenset({new_s.key, node_s.key, past_s.key}), new_face_key + 1))
    sub_space.face_type[f_new_2.key] = 1
    face.connect_spatial(f1r, f_new_1)
    face.connect_spatial(f_new_1, f1l)

    face.connect_spatial(f2r, f_new_2)
    face.connect_spatial(f_new_2, f2l)

    #
    face.connect_temporal(f_new_1, f_new_2)

    st.push(sub_space)


def decrease(st, node):
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

        sub_space.face_nodes[f.key] = frozenset(new_f_nodes)

    # connect the newly adjacent faces and remove the old face that used to be between them
    for f in face.faces(sub_space, faces_for_deletion):
        face.connect_spatial(f.left, f.right)
        sub_space.remove_face(f.key)

    sub_space.remove_key(left_s.key)

    # push the modified sub_space back in to the space_time
    st.push(sub_space)
