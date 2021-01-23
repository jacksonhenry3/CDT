class NodeObject(object):
    """This is just syntactic sugar to acces node relationships"""

    def __init__(self, st, node_id):
        super(NodeObject, self).__init__()
        self.st = st
        self.id = node_id

        if node_id in st.nodes:
            self.left = st.node_left[self.id]
            self.right = st.node_right[self.id]
            self.past = st.node_past[self.id]
            self.future = st.node_future[self.id]
            self.faces = st.faces_containing[self.id]
        else:
            # print("adding node " + str(self.id))
            st.nodes.append(self.id)

    def set_left(self, val):
        self.left = val
        self.st.node_left[self.id] = val

    def set_right(self, val):
        self.right = val
        self.st.node_right[self.id] = val

    def set_past(self, val):
        self.past = val
        self.st.node_past[self.id] = val

    def set_future(self, val):
        self.future = val
        self.st.node_future[self.id] = val

    def set_faces(self, val):
        self.faces = val
        self.st.faces_containing[self.id] = val
