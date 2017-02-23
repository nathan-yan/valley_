class Node:
    def __init__(self, name, type, is_output = False, parent = None, 
                 param_size = None, 
                 mode = None, 
                 subsample_x = 1, subsample_y = 1, path = ""):

        self.name = name 
        self.type = type
        self.is_output = is_output
        self.parents = [parent]

        self.param_size = param_size

        self.mode = mode 

        self.subsample_x = subsample_x 
        self.subsample_y = subsample_y 
    
        self.children = []
        self.path = path

        self.number = 0
            
    def add_child(self, name, type, is_output = False, param_size = None, mode = None, subsample_x = 1, subsample_y = 1, path = ""):
        self.children.append(Node(name = name, type = type, is_output = is_output, parent = self.name, param_size = param_size, mode = mode, subsample_x = subsample_x, subsample_y = subsample_y, path = path))
        return self.children[-1]    # return the new child
    
    def add_parent(self, parent):
        self.parents.append(parent)