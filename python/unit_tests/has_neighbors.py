def has_right_neightbor(node):
    return node.right != None


def has_left_neightbor(node):
    return node.left != None


def all_have_right_neightbor(st):
    has_neighbors = True
    for node in st.nodes.values():
        has_neighbors = has_neighbors and has_right_neightbor(node)
        if not has_neighbors:
            print(str(node) + " is missing a right neightbor")
    return has_neighbors


def all_have_left_neightbor(st):
    has_neighbors = True
    for node in st.nodes.values():
        has_neighbors = has_neighbors and has_left_neightbor(node)
        if not has_neighbors:
            print(str(node) + " is missing a left neightbor")
    return has_neighbors


def all_have_neighbors(st):
    left_neightborQ = all_have_left_neightbor(st)
    right_neighborQ = all_have_right_neightbor(st)
    return left_neightborQ and right_neighborQ
