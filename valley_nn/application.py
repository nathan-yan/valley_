import pygame
from pygame.locals import *

pygame.init()

from draw import*
import compiler

import collections

def main():
    screen = pygame.display.set_mode((2000, 2000))

    attributes = {'convolution' : ['filter size', 'subsample size', 'input channels', 'output channels'],
                  'matmul' : ['input size', 'output size'],
                  'ReLU' : [],
                  'PReLU' : ['alpha'],
                  'sigmoid' : [],
                  'tanh' : [],
                  'softmax' : [],
                  'flatten' : ['output dimensions'],
                  'variable' : ['initialization code'],
                  'placeholder' : ['shape'],
                  'categorical crossentropy' : [],
                  'gradient' : [],
                  'RMSprop' : ['lr', 'decay', 'epsilon'],
                  'SGD' : ['lr', 'momentum'],
                  'ADAM' : ['lr'],
                  'input' : ['path'],
                  'target' : ['path']}

    dependencies = {'convolution' : ['input', 'param'],
                    'matmul' : ['input', 'param'],
                    'ReLU' : ['input'],
                    'PReLU' : ['input'],
                    'sigmoid' : ['input'],
                    'tanh' : ['input'],
                    'softmax' : ['input'],
                    'flatten' : ['input'],
                    'variable': [],
                    'placeholder' : [],
                    'gradient' : ['optimizer', 'wrt'],
                    'categorical crossentropy': ['true distribution', 'predicted distribution'],
                    'RMSprop': ['loss'],
                    'SGD' : ['loss'],
                    'ADAM' : ['loss'],
                    'input' : [],
                    'target' : [],}

    colors = {'transform':[205, 50, 50],
              'activation':[100, 100, 150],
              'loss':[150, 150, 100],
              'operator':[50, 100, 50],
              'parameters':[100, 100, 100],
              'optimizer':[205, 130, 50],
              'misc':[204, 100, 60]}

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
              "RMSprop" : [colors['optimizer']],
              "SGD" : [colors['optimizer']],
              "ADAM" :  [colors['optimizer']],
              'input' : [colors['misc']],
              'target' : [colors['misc']]})

    font = ft.SysFont("Open Sans", 24)

    elements = []

    receiving = None

    running = True

    global_events = {'dragging':[None, [0, 0]]}

    while running:
        lost_focus_block = False                    # This is primarily for ContainerLayerWithAttributes, it blocks a lost focus if it's true.

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
                    print(compiler.compile(elements))

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
        for l in layers:
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

        for e in range(len(elements) - 1, -1, -1):
            elements[e].draw()

        pygame.display.flip()

if __name__ == "__main__":
    main()
