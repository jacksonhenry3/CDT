# this checks if in a flat space-time each node belongs to 6 simplices
def is_flat(st):
    for n in st.nodes:
        if not (st.get_faces_containing(n) == st.faces_containing[n]):
            return False
    return True


def is_valid_move(st, node, past, future):
    pass


# make sure there no duplicate faces or nodes


def push_pop(st, node):
    sub_space = st.pop(node)
    st.push(sub_space)
    # Check that this is the same as when starting
