# Compiler

def compile(objects):
    """
        compile(objects) -> order

        compile returns objects rearranged in the order they need to be processed in. If an element requires two other elements to be calculated before it, the two elements must appear before the main element in the code.

        compile also checks for dependencies--if the user hasn't filled out all dependencies, the compile returns
    """

    # Construct dependency/attribute list
    dependencies = {}
    attributes = {}

    for obj in objects:
        for button in obj.buttons:
            if button.num_dependencies > 0:
                return obj.text + '(' + obj.text_box.text + ') does not have all of its dependencies! Please fill in: ' + button.text

        dependencies[obj] = set()
        for con in obj.connections:
            dependencies[obj].add(con.parent)
        attributes[obj] = set(obj.attributes)

    # Create a list detailing the order in which the objects should be written

    order = []

    need_to_eliminate = set(objects)
    found_dependencies = set()
    while len(need_to_eliminate) > 0:
        delete_this_iteration = []

        for obj in need_to_eliminate:
            if obj not in found_dependencies:
                if dependencies[obj] == []:         # No dependencies
                    found_dependencies.add(obj)
                    delete_this_iteration.append(obj)

                    order.append(obj)
                elif dependencies[obj] <= found_dependencies:   # If all dependencies have already been found
                    found_dependencies.add(obj)
                    delete_this_iteration.append(obj)

                    order.append(obj)

        for obj in delete_this_iteration:
            need_to_eliminate.remove(obj)

    return order, attributes

def write(order, attributes, filename = 'compiled.py'):
    f = open(filename, 'w')

    f.write('# Importing modules\nimport theano\nimport theano.tensor as T\nimport numpy as np\n')

    for obj in order:
        print(order, 'order')
        name = clean_name(obj.text_box.text)

        dependencies = clean_dependencies(obj)
        attributes = {}
        for a in range(len(obj.text_boxes)):
            attributes[obj.attributes[a]] = obj.text_boxes[a].text

        if obj.text[:-4] == 'variable':
            f.write(name + " = theano.shared((" + attributes['initialization code'] + ").astype(np.float32))\n")

        elif obj.text[:-4] == 'matmul':
            f.write(name + " = T.dot(" + dependencies['input'][0] + ',' + dependencies['param'][0] + ')\n')

        elif obj.text[:-4] == 'convolution':
            f.write(name + " = T.nnet.conv2d(input = " + dependencies['input'][0] + ', filters = ' + dependencies['param'][0] + ', border_mode = "half")\n')

        elif obj.text[:-4] == 'ReLU':
            f.write(name + " = T.nnet.relu(" + dependencies['input'][0] + ')\n')

        elif obj.text[:-4] == 'softmax':
            f.write(name + " = T.nnet.softmax(" + dependencies['input'][0] + ')\n')

        elif obj.text[:-4] == 'tanh':
            f.write(name + " = T.tanh(" + dependencies['input'][0] + ')\n')

        elif obj.text[:-4] == 'sigmoid':
            f.write(name + " = T.nnet.sigmoid(" + dependencies['input'][0] + ')\n')

        elif obj.text[:-4] == 'placeholder':
            dims = int(attributes['dimensions'])

            if dim == 0:
                f.write(name + " = T.scalar()")
            elif dim == 1:
                f.write(name + ' = T.vector()')
            elif dim == 2:
                f.write(name + ' = T.matrix()')
            elif dim == 3:
                f.write(name + ' = T.tensor3()')
            elif dim == 4:
                f.write(name + ' = T.tensor4()')
            elif dim == 4:
                f.write(name + ' = T.tensor5()')
            #f.write(name + )

    f.close()

def clean_dependencies(obj):
    connections = {}
    for connection in obj.connections:
        if connection.position_tied:
            if connection.position_tied.text in obj.dependencies:
                if connections.get(connection):
                    connections[connection.position_tied.text].append(clean_name(connection.parent.text_box.text))
                else:
                    connections[connection.position_tied.text] = [clean_name(connection.parent.text_box.text)]

    return connections

def clean_name(name):
    build = ''
    numbers_at_end = ''

    numbers_in_beginning = True
    for char in name:
        if char not in '1234567890':
            numbers_in_beginning = False
            if char in '`~!@#$%^&*()_+-=\|[]{};:\'",.<>/?':
                build += '_'
            else:
                build += char
        elif char in '1234567890' and numbers_in_beginning:
            numbers_at_end += char
        elif char in '1234567890' and not numbers_in_beginning:
            build += char

    return build + numbers_at_end

print(clean_name("@conv_1/relu"))
