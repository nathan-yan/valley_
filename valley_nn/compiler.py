# Compiler

def compile(objects):
    # Construct dependency/attribute list
    dependencies = {}
    attributes = {}

    for obj in objects:
        dependencies[obj] = set()
        for con in obj.connections:
            dependencies[obj].add(con.parent)
        attributes[obj] = set(obj.attributes)

    # Create a list detailing the order in which the objects should be written

    order = []

    need_to_eliminate = set(objects)
    found_dependencies = set()
    while len(need_to_eliminate) > 0:
        print(len(need_to_eliminate), found_dependencies)
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

    for o in order:
        print(o.text_box.text)

    return order

def write(dependencies, attributes, order, filename = 'compiled.valley'):
    f = open(filename, 'w')

    for obj in order:
        if obj.text == 'matmul':
            deps = dependencies[obj]


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
