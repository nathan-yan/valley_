import node 
from node import Node

class Text:
    def __init__(self):
        self.text = ""

    def add(self, add, newline = True):
        self.text += '\n' * newline + add 

class Queue:
    def __init__(self):
        self.queue = []
    
    def add(self, object):
        self.queue.append(object)
    
    def pop(self):
        return_ = self.queue[0]
        del self.queue[0]
        return return_

    def isEmpty(self):
        return not self.queue 

"""
n1 = Node(name = 'inp', type = "INPUT")
n1_1 = n1.add_child(name = 'conv1_1', type = 'conv', param_size = (32, 3, 28, 28), mode = "half")
n1_2 = n1.add_child(name = 'conv1_2', type = 'conv', param_size = (64, 3, 28, 28), mode = "half")
n1_1.add_child(name = 'conv1_relu', type = 'relu')
n1_2.add_child(name = 'conv1_relu', type = 'relu')
loss = n1_2.add_child(name = 'loss', type = 'mse_loss', is_output = True)
grad = loss.add_child(name = 'grad_loss', type = 'grad')
grad.add_parent("params[0]")
"""

def compile_graph(data_dim, target_dim, root):
    # Given a tree, create a theano file that will implement the neural network
    # Every layer will be a class with a name, data_size, type, as well as parent name
    """Tree()
    a tree's root will be input. Every child of every node is a layer that takes its parent
    as input.
    """
    

    if root == "Can't build tree! ":
        return "Can't build graph (tree compile failed)"

    write = Text()
    write.add("import theano")
    write.add("import numpy")
    write.add("import load")
    write.add("import theano.tensor as T")
    write.add("from theano.sandbox.rng_mrg import MRG_RandomStreams as RandomStreams")
    write.add("import numpy as np")
    write.add("from theano.tensor.nnet.conv import conv2d")
    write.add("from theano.tensor.signal.downsample import max_pool_2d")
    write.add("srng = RandomStreams()")

    write.add("def init_weights(shape):")
    write.add("    return theano.shared(np.random.randn(*shape) * 0.01)")

    write.add("params = []")    # our parameters

    if data_dim > 2:
        write.add(root.name + " = T.tensor" + str(data_dim) + "()")
    else:
        if data_dim == 1:
            write.add(root.name + " = T.vector()")
        elif data_dim == 2:
            write.add(root.name + "= T.matrix()")
    
    
    # Start writing the model
    # We start with the children of the root because root is inp
    # This is essentially breadth first search
    
    queue = Queue()
    queue.add(root)
    
    assessment_order = []   # We perform a single BFS of the tree, and store the order at which we assess the tree, so we can just iterate through this next time 
    output_variables = []
    grad_variables = []
    grad_variables_text = []
    grad_variables_text_ = {}
    param_variables = []

    loss_ = ""
    params_text = []

    variable_name = "inp"   # since inp is our root, we will always start out with this
    variable_names = []

    target_path = None 

    while not queue.isEmpty(): 
        node = queue.pop()  # pop out a layer 
        #if node.param_size != None:
            #write.add("params.append(init_weights(" + str(node.param_size) + "))")
        
        if node.name not in variable_names:

            if node.is_output:
                output_variables.append(node.name)
            
            if node.type == 'gradient':
                grad_variables.append(node.name)
            
            if node.type == 'target':
                target_path = node.name
                if target_dim > 2:
                    write.add(node.name + " = T.tensor" + str(target_dim) + "()")
                else:
                    if target_dim == 1:
                        write.add(node.name + " = T.vector()")
                    elif target_dim == 2:
                        write.add(node.name + " = T.matrix()")


            assessment_order.append(node)
            print len(assessment_order)
            if len(assessment_order) > 1000:      # Seriously, who's actually gonna build a network this big
                return "Network didn't compile! (depth exceeded)"

            for child in node.children:
                #print queue.queue
                queue.add(child)       
        
        variable_names.append(node.name)

    variable_names = []

    inp_path = root.path

    for i in params_text:
        write.add(i)

    param_idx = 0

    if target_path == None:
        return "Couldn't find a target path (graph compile failed)"

    assessment_order = assessment_order[:]
    print [assessment_order[i].name for i in range (len(assessment_order))]    
    while assessment_order != []:
        stuff_to_delete = []

        for node in assessment_order:
            
            if node.name not in variable_names:
                check = True
                for parent in node.parents:
                    if parent in [assessment_order[i].name for i in range (len(assessment_order))]:
                        check = False
                
                if check:
                    try:
                        if node.type == "relu":
                        # print node.name, node.parents[0]
                            write.add(node.name + "=T.nnet.relu(" + node.parents[0] + ")")
                        elif node.type == "sigmoid":
                            write.add(node.name + "=T.nnet.sigmoid(" + node.parents[0] + ")")
                        elif node.type == "conv":
                        # print node.parents[0], param_idx, node.mode, node.subsample_x, node.subsample_y

                            write.add(node.name +\
                                    "=T.nnet.conv2d(input = " + node.parents[0] +\
                                    ", filters = " + assessment_order[assessment_order.index(node) - 1].name +\
                                    ",border_mode = '" + node.mode + "'" +\
                                    ",subsample=(" + str(node.subsample_x) + "," + str(node.subsample_y) + "))")
                            
                            param_idx += 1

                        elif node.type == "gradient":
                            cost = not "loss" in node.parents[0]
                            wrt = not cost

                            grad_variables_text_[node.parents[wrt]] = node.name
                            grad_variables_text.append(node.name +\
                                    "=T.grad(cost = " + node.parents[cost] +\
                                    ", wrt = " + node.parents[wrt] + ")")

                        elif node.type == "mse_loss":
                            write.add(node.name +\
                                    "=T.mean(T.sum((" + node.parents[0] + " - " + node.parents[1] + ") ** 2, axis = -1))")

                        elif node.type == "param":
                            write.add(node.name +\
                                    "= init_weights(" + str(node.param_size) + ")")
                            write.add("params.append(" + str(node.name) + ")")
                            param_variables.append(node.name)
                        
                        elif node.type == "flatten":
                            write.add(node.name +\
                                    "= T.flatten(" + str(node.parents[0]) +\
                                    ", outdim = 2)")
                        
                        elif node.type == "matmul":
                            write.add(node.name +\
                                    "= T.dot(" + node.parents[0] +\
                                    ", " + assessment_order[assessment_order.index(node) - 1].name +\
                                    ")")
                        
                        elif node.type == "target":
                            target_path_ = node.path

                            param_idx += 1 

                        elif node.type == 'output':
                            output_variables.append(node.parents[0])

                        elif node.type == 'merge':
                            write.add(node.name +\
                                        " = T.concatenate(" + str(node.parents).replace("'", '') +\
                                        ", axis = " + str(node.param_size[0]) + ")")
                        elif node.type == 'split':
                            write.add(node.name +\
                                        " =" + str(node.parents[0]) + node.param_size)
                    except TypeError:
                        p = "parents, name - " + str(node.parents) + " " + str(node.name)

                        return "Type error, make sure all your forms are filled (" + p + ")"
                    
                    stuff_to_delete.append(assessment_order[assessment_order.index(node)])
                    variable_names.append(node.name)
        assessment_order = [a for a in assessment_order if a not in stuff_to_delete]            

    for i in grad_variables_text:
        write.add(i)

    write.add("updates = []")

    gradients = []
    for p in param_variables:
        gradients.append(grad_variables_text_[p])

    write.add("for p, g in zip(" + str(param_variables).replace("'", '') + ", " + str(gradients).replace("'", '') + "):")
    write.add("    updates.append([p, p - g * 0.01])")
    write.add("train = theano.function(inputs = [" + root.name + "," +  target_path+ "], outputs = " + str(output_variables).replace("'", '') + ", updates = updates)")

    write.add("mnist = load.MNIST()")
    write.add("X, y = mnist.load_training()")
    write.add("for epoch in range (100):")
    write.add("    for batch in range (0, X.shape[0], 50):")
    write.add("        " + str(output_variables).replace("'", '') + " = train(X[batch:batch+50], y[batch:batch+50])")
    write.add("        if batch % 1000 == 0:")
    write.add("            print " + str(output_variables).replace("'", ''))    
    
    file = open("compile.theano", 'w')
    file.write(write.text)
    file.close()
    return 0;

#compile_graph(4, 3, n1)


