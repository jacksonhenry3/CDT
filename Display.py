import numpy as np
def show_simplex_adjacency_matrix(st):
    # This visualizes the simplex ajacency matrix
    
    data = []
    row = []
    col = []
    
    
    #each simplex maps to a unique ID
    idx = 0
    map = {}
    
    #Loop through each simplex
    for i in st.faces:
        map[i] = idx #generate the map
        idx += 1
        connections = st.face_x[i] #Get both spatial connections 
        for c in connections:
            row.append(i) #add face i (a,b,c) 
            col.append(c) #add face c to cols
            data.append(1) #The values of the connection between c and i
            
        #repeat the process for the time like connection
        connections = st.face_t[i]
    
        row.append(i)
        col.append(connections)
        data.append(2)
    
    for i in range(len(data)):
        # print(col[i])
        row[i] = map[row[i]]
        col[i] = map[col[i]]
    
    dense_dat = np.zeros((len(st.faces),len(st.faces)))
    for i in range (len(data)):
        dense_dat[col[i],row[i]] = data[i]
    
    
    
    
    import matplotlib.pyplot as plt
    plt.imshow(dense_dat,interpolation="none")
    plt.show()
    
def show_vertex_adjacency_matrix(st):
    # This visualizes the vertex ajacency matrix
    
    data = []
    row = []
    col = []
    
    #Loop through each simplex
    for i in st.nodes:
        connections = st.node_x[i] #Get both spatial connections 
        for c in connections:
            row.append(i) #add vertex i to rows 
            col.append(c) #add vertex c to cols
            data.append(1) #The values of the connection between c and i
            
        #repeat the process for the time like connection
        connections = st.node_t[i] #Get both spatial connections 
        for c in connections:
            row.append(i) #add vertex i to rows
            col.append(c) #add vertex c to cols
            data.append(2) #The values of the connection between c and i
    
    
    dense_dat = np.zeros((len(st.nodes),len(st.nodes)))
    for i in range (len(data)):
        dense_dat[col[i],row[i]] = data[i]
    
    
    
    
    import matplotlib.pyplot as plt
    plt.imshow(dense_dat,interpolation="none")
    plt.show()
