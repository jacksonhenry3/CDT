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


    def __getattr__(self, item):

        attr = {'left': self.node_left[self.id],
                'right': self.node_right[self.id]}.get(item, None)
        if attr is None:
            return self.__dict__.get(item)

    def __setattr__(self, key, value):
        {'left': self.node_left}.get(key)[self.id] = value.id if isinstance(value, NodeObject) else value

    def set_left(self, val):
        self.left = val
        self.st.node_left[self.id] = val

    def set_right(self, val):
        self.right = val
        self.st.node_right[self.id] = val

    def set_past(self, val):
        self.past = val
        self.st.node_past[self.id] = val
        for n in val:
            if self.id not in self.st.node_future[n]:
                self.st.node_future[n].append(self.id)

    def set_future(self, val):
        self.future = val
        self.st.node_future[self.id] = val
        for n in val:
            if self.id not in self.st.node_past[n]:
                self.st.node_past[n].append(self.id)

    def set_faces(self, val):
        self.faces = val
        self.st.faces_containing[self.id] = val
