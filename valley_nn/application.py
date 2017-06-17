import pygame
from pygame.locals import *

pygame.init()

from draw import*
import compiler

import collections

def main():
    screen = pygame.display.set_mode((2000, 2000))

    attributes = {'convolution' : ['filter size', '', 'subsample size', '2, 2', 'input channels', '', 'output channels', ''],
                  'matmul' : ['input size', '', 'output size', ''],
                  'ReLU' : [],
                  'PReLU' : ['alpha', '0.1'],
                  'sigmoid' : [],
                  'tanh' : [],
                  'softmax' : [],
                  'flatten' : ['output dimensions', '2'],
                  'variable' : ['initialization code', ''],
                  'placeholder' : ['dimensions', ''],
                  'categorical crossentropy' : [],
                  'mean squared error' : [],
                  'gradient' : [],
                  'RMSprop' : ['lr', '0.01', 'rho', '0.9', 'decay', '0.0', 'epsilon', '1e-8'],
                  'SGD' : ['lr', '0.01', 'momentum', '0.0'],
                  'ADAM' : ['lr', '0.01'],
                  'L1 regularization' : ['scaling factor', '1e-4'],
                  'L2 regularization' : ['scaling factor', '1e-4'],
                  'input' : ['path', '', 'dimensions', ''],
                  'target' : ['path', '', 'dimensions', '']}

    dependencies = {'convolution' : {'input' : 1, 'param' : 1},
                    'matmul' : {'input' : 1, 'param' : 1},
                    'ReLU' : {'input' : 1},
                    'PReLU' : {'input' : 1},
                    'sigmoid' : {'input' : 1},
                    'tanh' : {'input' : 1},
                    'softmax' : {'input' : 1},
                    'flatten' : {'input' : 1},
                    'variable': {},
                    'placeholder' : {},
                    'gradient' : {'optimizer' : 1, 'wrt' : -1},
                    'categorical crossentropy': {'true distribution' : 1, 'predicted distribution' : 1},
                    'mean squared error' : {'true distribution' : 1, 'predicted distribution' : 1},
                    'RMSprop': {'loss' : 1},
                    'SGD' : {'loss' : 1},
                    'ADAM' : {'loss' : 1},
                    'L1 regularization' : {'weights' : 1},
                    'L2 regularization' : {'weights' : 1},
                    'input' : {},
                    'target' : {},}

    colors = {'transform':[180, 50, 50],
              'activation':[100, 50, 100],
              'loss':[80, 80, 50],
              'operator':[50, 100, 50],
              'parameters':[100, 100, 100],
              'optimizer':[175, 110, 50],
              'misc':[184, 90, 60],
              'regularization' : [60, 80, 100]}

    layers = collections.OrderedDict({"convolution" : [colors['transform']],
              "matmul" : [colors['transform']],
              "ReLU" : [colors['activation']],
              "PReLU" : [colors['activation']],
              "sigmoid" : [colors['activation']],
              "tanh" : [colors['activation']],
              "softmax" : [colors['activation']],
              "flatten" : [colors['operator']],
              "variable" : [colors['parameters']],
              "placeholder" : [colors['parameters']],
              "gradient" : [colors['parameters']],
              "categorical crossentropy" : [colors['loss']],
              "mean squared error" : [colors['loss']],
              "RMSprop" : [colors['optimizer']],
              "SGD" : [colors['optimizer']],
              "ADAM" :  [colors['optimizer']],
              "L1 regularization" : [colors['regularization']],
              "L2 regularization" : [colors['regularization']],
              'input' : [colors['misc']],
              'target' : [colors['misc']]})

    layer_names = ['convolution', 'matmul', 'ReLU', 'PReLU', 'sigmoid', 'tanh' , 'softmax', 'flatten', 'variable', 'placeholder', 'gradient', 'categorical crossentropy', 'mean squared error', 'RMSprop', 'SGD', 'ADAM', "L1 regularization", 'L2 regularization', 'input', 'target']

    font = ft.SysFont("Open Sans", 24)

    # List of all the major elements to keep track of
    elements = []

    # Which element is currently receiving events. It's kind of an inception-y kind of deal where the main element recieves events from the program, and then the element passes those events further down to its objects
    receiving = None

    # Is the application running?
    running = True

    # Global events to keep track of, first element is the element which is being dragged, second is position (I don't think I use the position)
    global_events = {'dragging':[None, [0, 0]]}

    while running:
        lost_focus_block = False      # This is primarily for ContainerLayerWithAttributes, it blocks a lost focus if it's true.

        # Keeps track of events that have happened in this frame, first element is if there was a click, second element is position (I don't think i use the position)
        events_this_frame = {'click':[False, None], '':''}

        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if receiving:
                receiving.receive_event(event)

            if event.type == pygame.QUIT:
                running = False
                pygame.quit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    for e in elements:
                        e.alter_position([e.pos[0], e.pos[1] - 100])
                elif event.key == pygame.K_UP:
                    for e in elements:
                        e.alter_position([e.pos[0], e.pos[1] + 100])
                elif event.key == pygame.K_RIGHT:
                    for e in elements:
                        e.alter_position([e.pos[0] - 100, e.pos[1]])
                elif event.key == pygame.K_LEFT:
                    for e in elements:
                        e.alter_position([e.pos[0] + 100, e.pos[1]])

                elif event.key == pygame.K_DELETE:
                    if receiving:
                        if isinstance(receiving, ContainerLayer):
                            del elements[elements.index(receiving)]
                        receiving = None

                elif event.key == pygame.K_ESCAPE:
                    compiled = compiler.compile(elements)

                    if len(compiled) != 2:
                        print(compiled)
                    else:
                        compiler.write(compiled[0], compiled[1])

            elif event.type == pygame.MOUSEBUTTONDOWN:
                clicked_on_object = False
                events_this_frame['click'] = [True, list(pygame.mouse.get_pos())]

                if receiving:
                    for obj in receiving.objects:
                        if obj.click(pygame.mouse.get_pos()):
                            lost_focus_block = True
                            break;

            elif event.type == pygame.MOUSEBUTTONUP:
                if global_events['dragging'][0]:
                    global_events['dragging'][0].on_letgo(elements)
                global_events['dragging'] = [None, [0, 0]]

            #elif event.type == pygame.MOUSEBUTTONDOWN:

        if global_events['dragging'][0]:
            global_events['dragging'][0].alter_position(np.array(pygame.mouse.get_pos()) - global_events['dragging'][1])

        rect = [30, 50]

        # Draw the menu on the side
        for l in layer_names:
            r = font.render(l, [255, 255, 255])[0]
            text_rect = r.get_rect()
            rRect(surface = screen, rect = [rect[0] - 10, rect[1] - 10, text_rect[2] + 20, text_rect[3] + 20], color = layers[l][0])

            if pygame.rect.Rect([rect[0] - 10, rect[1] - 10, text_rect[2] + 20, text_rect[3] + 20]).collidepoint(pygame.mouse.get_pos()) and events_this_frame['click'][0]:
                add(elements, ContainerLayerWithDependencies(screen, pos = [rect[0] - 10, rect[1] - 10], color = layers[l][0], text = l + ' :: ', attributes = attributes[l], dependencies = dependencies[l]))

                global_events['dragging'][0] = elements[-1]
                elements[-1].is_editing = True

            screen.blit(r, rect)

            rect[1] += text_rect[3] + 30


        for e in elements:
            for o in e.objects:
                if o.click(pygame.mouse.get_pos()):
                    # Connectors are a bit of a special case
                    if isinstance(global_events['dragging'][0], Connector) and o != global_events['dragging'][0] and o.connectable:
                        if isinstance(o, ContainerLayerWithDependencies):
                            if o.num_dependencies == 0:
                                global_events['dragging'][0].rejected = True

                        global_events['dragging'][0].alter_position([o.pos[0] + o.rect[2]/2, o.pos[1] + o.rect[3] + 10 * global_events['dragging'][0].scale])

                    if events_this_frame['click'][0]:
                        receiving = o
                        o.on_click()

                        if not global_events['dragging'][0]:
                            global_events['dragging'][0] = o
                            global_events['dragging'][1] = np.array(pygame.mouse.get_pos()) - np.array(o.pos)
                    else:
                        o.on_hover()
                else:
                    if events_this_frame['click'][0] and not lost_focus_block:
                        o.lost_focus()


        # drawing of elements is final because there is some iteration-based clean up in draw
        for e in range(len(elements) - 1, -1, -1):
            elements[e].draw()

        pygame.display.flip()

if __name__ == "__main__":
    main()
