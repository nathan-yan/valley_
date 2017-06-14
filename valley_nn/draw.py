import pygame
from pygame.locals import *
from pygame import gfxdraw

import pygame.freetype as ft
import ctypes

import numpy as np

import time

import copy

pygame.init()
pygame.key.set_repeat(1000, 50)

ctypes.windll.user32.SetProcessDPIAware()
true_res = (ctypes.windll.user32.GetSystemMetrics(), ctypes.windll.user32.GetSystemMetrics(1))

class Container(object):
    def __init__(self, surface, pos, color, text = '', font = 'Open Sans', padding = [10, 10, 10, 10]):
        self.scale = 2
        self.surface = surface

        self.text = text
        self.font = ft.SysFont(font, 12 * self.scale)
        self.display_text = self.font.render(self.text, (255, 255, 255))[0]
        self.text_rect = self.display_text.get_rect()
        self.rect = pygame.rect.Rect([0, 0, 0, 0])

        self.original_color = [color[0], color[1], color[2]]
        self.color = color
        self.objects = [self]

        self.original_padding = np.array(padding)
        self.padding = self.original_padding * self.scale         # top right bottom left

        self.prescale_pos = pos
        self.pos = copy.deepcopy(pos)

        self.connectable = False

    def alter_scale(self, new_scale):
        self.pos = [self.pos[0] + self.prescale_pos[0] * (new_scale - self.scale), self.pos[1] + self.prescale_pos[1] * (new_scale - self.scale)]
        self.scale = new_scale

        self.update()

    def alter_position(self, new_pos):
        self.pos = copy.deepcopy(list(new_pos))
        self.prescale_pos = np.array(copy.deepcopy(list(new_pos)))

    def draw(self, pos = None):
        if pos != None:
            self.rect = pygame.rect.Rect([pos[0], pos[1], self.text_rect[2] + self.padding[1] + self.padding[-1], self.text_rect[3] + self.padding[0] + self.padding[2]])
            rRect(self.surface, self.rect, self.color)

            self.surface.blit(self.display_text, [pos[0] + self.padding[1], pos[1] + self.padding[0]])
        else:
            self.rect = pygame.rect.Rect([self.pos[0], self.pos[1], self.text_rect[2] + self.padding[1] + self.padding[-1], self.text_rect[3] + self.padding[0] + self.padding[2]])
            rRect(self.surface, self.rect, self.color)

            self.surface.blit(self.display_text, [self.pos[0] + self.padding[1], self.pos[1] + self.padding[0]])

        self.color = copy.deepcopy(self.original_color)

    def click(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

    def on_click(self):
        pass

    def on_hover(self):
        self.color = [self.original_color[0] - 50, self.original_color[1] - 50, self.original_color[2] - 50]

    def on_letgo(self, extra_info):
        pass

    def on_connection(self):
        pass

    def lost_focus(self):
        pass

    def receive_event(self, e):
        pass

    def update(self):
        self.font.size = 12 * self.scale
        self.display_text = self.font.render(self.text, (255, 255, 255))[0]
        self.text_rect = self.display_text.get_rect()

        self.padding = self.original_padding * self.scale

class ContainerNameEditable(Container):
    def __init__(self, surface, pos, color, text = '', font = 'Open Sans', padding = [10, 10, 10, 10]):
        super().__init__(surface, pos, color, text, font, padding)

        self.text_box = textBox(surface, copy.deepcopy(pos), [150, 206, 250], "GenericName", font, padding = [10, 0, 0, 10])

        # objects should be ordered depending on click-priority: first item has largest priority
        self.objects = [self, self.text_box]

    def draw(self):
        self.rect = pygame.rect.Rect([self.pos[0], self.pos[1],
                                 self.text_rect[2]  + self.text_box.text_rect[2] + self.text_box.padding[-1] +
                                 self.padding[1],
                                 self.text_rect[3] + self.padding[0] + self.padding[2]])

        rRect(self.surface, self.rect, self.color)

        self.surface.blit(self.display_text, [self.pos[0] + self.padding[1], self.pos[1] + self.padding[0]])

        self.text_box.draw(pos = [self.pos[0] + self.padding[1] + self.text_rect[2], self.pos[1]])

        self.color = copy.deepcopy(self.original_color)

    def update(self):
        super().update()
        self.text_box.alter_scale(self.scale)

class Connector(Container):
    def __init__(self, surface, parent):
        self.scale = 2

        self.surface = surface

        self.parent = parent
        self.radius = 3 * self.scale

        parent_rect = self.parent.rect
        self.connectable = False

        self.pos = [parent_rect[0] + parent_rect[2] / 2, parent_rect[1] - 10 * self.scale]
        self.moved = False
        self.moving = True

        self.order = 0

        self.connected_to = self.parent

        self.color = [200, 200, 200]

        self.objects = [self]

        self.rejected = False

    def alter_scale(self, new_scale):
        self.scale = new_scale
        self.radius = 3 * self.scale

    def receive_event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_DELETE:
                if self.connected_to != self.parent and self.connected_to != None:
                    self.connected_to.connections.remove(self)
                    self.connected_to = None

                del self.parent.objects[self.parent.objects.index(self)]

    def click(self, mouse_pos):
        return np.sqrt((self.pos[0] - mouse_pos[0]) ** 2 + (self.pos[1] - mouse_pos[1]) ** 2) < (self.radius + 2 * self.scale)

    def on_click(self):
        self.moved = True
        self.moving = True

    def on_hover(self):
        self.color = [150, 150, 150]

    def on_connection(self, element):
        self.element.connections.append(self)

    def on_letgo(self, extra_info):
        self.moving = False

        parent_rect = self.parent.rect

        # Connector returned to its original position
        if self.pos == [parent_rect[0] + parent_rect[2] / 2, parent_rect[1] + parent_rect[3] + 10 * self.scale]:
            self.moved = False

        m = True
        for connector in self.parent.objects:
            if isinstance(connector, Connector):
                m &= connector.moved
        if m == True:
            self.parent.objects.append(Connector(self.surface, self.parent))
            self.parent.objects[-1].alter_scale(self.parent.scale)

        print(self.pos)

        found = False
        for e in extra_info:

            if e.connectable:
                if [int(self.pos[0]), int(self.pos[1])] == [int(e.pos[0] + e.rect[2]/2), int(e.pos[1] + e.rect[3] + 10 * self.scale)]:
                    if not self.rejected:
                        self.connected_to = e
                        e.connections.add(self)
                        found = True

                        e.on_got_connection()

                        break;
                    else:
                        self.rejected = False

        if not found and self.connected_to and self.connected_to != self.parent:
            self.connected_to.connections.remove(self)
            self.connected_to.on_lost_connection()

            self.connected_to = None

    def draw(self):
        if (self.connected_to != self.parent and self.connected_to != None and self.moving == False):
            parent_rect = self.connected_to.rect
            self.pos = [parent_rect[0] + parent_rect[2] / 2+ self.order * 10 * self.scale, parent_rect[1] + parent_rect[3] + 10 * self.scale]
        elif (self.connected_to == self.parent and self.moved == False):
            self.pos = [self.parent.rect[0] + self.parent.rect[2] / 2 , self.parent.rect[1] - 10 * self.scale]
        else:
            pass

        parent_rect = self.parent.rect

        pygame.draw.aaline(self.surface, (255, 255, 255), self.pos, [parent_rect[0] + parent_rect[2] / 2, parent_rect[1]], 1)

        if self.rejected:
            aaCircle(self.surface, [255, 100, 100], self.pos, radius = self.radius)
        else:
            aaCircle(self.surface, self.color, self.pos, radius = self.radius)
        aaCircle(self.surface, [100, 200, 100], self.pos, radius = self.radius, filled = False)

        self.color = [200, 200, 200]

class ContainerLayer(ContainerNameEditable):
    def __init__(self, surface, pos, color, text = '', font = 'Open Sans', padding = [10, 10, 10, 10]):
        super().__init__(surface, pos, color, text, font, padding)

        # objects should be ordered depending on click-priority: last item has largest priority
        self.objects = [self, self.text_box, Connector(self.surface, self)]
        self.connections = set()

        self.connectable = True

    def receive_event(self, e):
        super().receive_event(e)

        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_DELETE:
                for obj in self.objects:
                    if isinstance(obj, Connector):
                        obj.receive_event(e)

                for connection in self.connections:
                    connection.connected_to = None

    def draw(self):
        self.rect = pygame.rect.Rect([self.pos[0], self.pos[1],
                                 self.text_rect[2]  + self.text_box.text_rect[2] + self.text_box.padding[-1] +
                                 self.padding[1],
                                 self.text_rect[3] + self.padding[0] + self.padding[2]])

        rRect(self.surface, self.rect, self.color)

        self.surface.blit(self.display_text, [self.pos[0] + self.padding[1], self.pos[1] + self.padding[0]])

        self.text_box.draw(pos = [self.pos[0] + self.padding[1] + self.text_rect[2], self.pos[1]])
        for connector in self.objects:
            if isinstance(connector, Connector):
                connector.draw()

        self.color = copy.deepcopy(self.original_color)

    def on_got_connection(self):
        self.total_connections = len(self.connections)

        connections = [self.objects[_] for _ in range (len(self.objects)) if isinstance(self.objects[_], Connector)]

        counter = 0
        for c in self.connections:
            c.order = -(self.total_connections - 1)/2 + counter
            counter += 1

    def on_lost_connection(self):
        self.on_got_connection()

    def update(self):
        super().update()
        self.text_box.alter_scale(self.scale)
        for connector in self.objects:
            if connector != self:
                connector.alter_scale(self.scale)

class ContainerLayerWithAttributes(ContainerLayer):
    def __init__(self, surface, pos, color, text = '', font = 'Open Sans', padding = [10, 10, 10, 10], attributes = []):
        super().__init__(surface, pos, color, text, font, padding)

        self.attributes = attributes
        self.text_boxes = [textBox(self.surface, [0, 0], color = [255, 255, 255], text = 'required', padding = [20, 10, 10, 10]) for box in range (len(self.attributes))]

        self.objects += self.text_boxes
        self.is_editing = False

        self.last_click = time.time()

    def receive_event(self, e):
        super().receive_event(e)

        if e.type == pygame.MOUSEBUTTONDOWN:
            if time.time() - self.last_click < .5:
                self.is_editing = not self.is_editing

            self.last_click = time.time()

    def draw(self):
        super().draw()

        if self.is_editing:
            pos = [self.pos[0], self.pos[1] + self.rect[3]]
            for box in range(len(self.text_boxes)):
                query = self.font.render(self.attributes[box] + ':', [255, 255, 255])[0]
                self.surface.blit(query, [pos[0], pos[1] + self.text_boxes[box].padding[0]])
                self.text_boxes[box].draw([pos[0] + query.get_rect()[2], pos[1]])

                pos[1] += 40

class ContainerLayerWithDependencies(ContainerLayerWithAttributes):
    def __init__(self, surface, pos, color, text = '', font = 'Open Sans', padding = [10, 10, 10, 10], attributes = [], dependencies = []):
        super().__init__(surface, pos, color, text, font, padding, attributes)

        self.dependencies = dependencies

        self.buttons = [Button(self.surface, self, text = '__' + dependence, offset = [100, 0]) for dependence in self.dependencies]

        self.objects += self.buttons

        if self.dependencies == []:
            self.num_dependencies = 100000
        else:
            self.num_dependencies = len(self.buttons)

    def draw(self):
        if self.is_editing:
            pos = [self.pos[0], self.pos[1] + self.rect[3]]
            for box in range(len(self.text_boxes)):
                query = self.font.render(self.attributes[box] + ':', [255, 255, 255])[0]
                self.surface.blit(query, [pos[0], pos[1] + self.text_boxes[box].padding[0]])
                self.text_boxes[box].draw([pos[0] + query.get_rect()[2], pos[1]])

                pos[1] += 40

        pos = [self.pos[0] + self.padding[-1], self.pos[1] + self.padding[0] + self.text_rect[3] + 10]

        for button in self.buttons:

            pos[0] += button.text_rect[2] + button.padding[-1]

        if self.buttons:
            height = self.buttons[0].text_rect[-1]
        else:
            height = 0

        self.rect = pygame.rect.Rect([self.pos[0], self.pos[1],
                                 self.text_rect[2]  + self.text_box.text_rect[2] + self.text_box.padding[-1] +
                                 self.padding[1],
                                 self.text_rect[3] + self.padding[0] + self.padding[2] + height])

        hang = min(self.pos[0] + self.rect[2] - pos[0], 0)
        self.rect[2] -= hang

        rRect(self.surface, self.rect, self.color)

        self.surface.blit(self.display_text, [self.pos[0] + self.padding[1], self.pos[1] + self.padding[0]])

        self.text_box.draw(pos = [self.pos[0] + self.padding[1] + self.text_rect[2], self.pos[1]])
        for connector in self.objects:
            if isinstance(connector, Connector):
                connector.draw()

        self.color = copy.deepcopy(self.original_color)

        pos = [self.pos[0] + self.padding[-1], self.pos[1] + self.padding[0] + self.text_rect[3] + 10]

        for button in self.buttons:
            lower = 13 - button.text_rect[-1]
            button.draw([pos[0], pos[1] + lower + 3])
            pos[0] += button.text_rect[2] + button.padding[-1]

    def on_got_connection(self):
        self.total_connections = len(self.connections)

        connections = [self.objects[_] for _ in range (len(self.objects)) if isinstance(self.objects[_], Connector)]

        counter = 0
        for c in self.connections:
            c.order = -(self.total_connections - 1)/2 + counter
            counter += 1

        self.num_dependencies -= 1

    def on_lost_connection(self):
        super().on_lost_connection()
        self.num_dependencies += 1

class Button(Container):
    def __init__(self, surface, parent, pos = [0, 0], color = [255, 255, 255], text = '', font = 'Open Sans', padding = [10, 10, 10, 10], offset = [0, 0]):
        super().__init__(surface, pos, color, text, font, padding)
        self.parent = parent

        self.color = [255, 255, 255]
        self.original_color = [255, 255, 255]

        self.text = text
        self.font = ft.SysFont(font, 8 * self.scale)
        self.display_text = self.font.render(self.text, self.color)[0]
        self.text_rect = self.display_text.get_rect()

        self.pos = [self.parent.pos[0] + offset[0], self.parent.pos[1] + offset[1]]
        self.offset = offset

        self.color = color

    def draw(self, pos = None):
        if pos:
            self.pos = pos
        else:
            self.pos = [self.parent.pos[0] + self.offset[0], self.parent.pos[1] + self.offset[1]]

        self.rect = pygame.rect.Rect(self.pos + [self.text_rect[2], self.text_rect[3]])

        self.surface.blit(self.display_text, self.pos)

        if self.color != self.original_color:
            self.color = copy.deepcopy(self.original_color)
            self.update()

    def on_hover(self):
        self.color = [self.original_color[0] - 50, self.original_color[1] - 50, self.original_color[2] - 50]

        self.update()

    def update(self):
        self.font.size = 8 * self.scale
        self.display_text = self.font.render(self.text, self.color)[0]
        self.text_rect = self.display_text.get_rect()

        self.padding = self.original_padding * self.scale

class textBox(Container):
    def __init__(self, surface, pos, color, text = '', font = 'Open Sans', padding = [10, 10, 10, 10]):
        super().__init__(surface, pos, color, text, font, padding)
        self.is_editing = False
        self.cursor = 0                 # Typing a letter would mean inserting the first letter

        self.font = ft.SysFont(font, 12 * self.scale)
        self.display_text = self.font.render(self.text, color)[0]
        self.text_rect = self.display_text.get_rect()

    def draw(self, pos = None):
        if self.is_editing:
            if pos != None:
                self.pos = pos
                # Render the first part
                first = self.font.render(self.text[:self.cursor] + 'l', self.color)[0]
                second = self.font.render('l' + self.text[self.cursor:], self.color)[0]

                self.surface.blit(first, [pos[0] + self.padding[1], pos[1] + self.padding[0]])
                x, y = pos[0] + self.padding[1] + first.get_rect()[2], pos[1] + self.padding[0]

                self.surface.blit(second, [x, pos[1] + self.padding[0]])
                pygame.draw.line(self.surface, (self.color), (x, y - 5), (x, y + first.get_rect()[-1]), int(3 * self.scale))

            else:
                self.surface.blit(self.display_text, [self.pos[0] + self.padding[1], self.pos[1] + self.padding[0]])

        else:
            if pos != None:
                self.pos = pos
                self.surface.blit(self.display_text, [pos[0] + self.padding[1], pos[1] + self.padding[0]])
            else:
                self.surface.blit(self.display_text, [self.pos[0] + self.padding[1], self.pos[1] + self.padding[0]])

        if self.color != self.original_color:
            self.color = self.original_color
            self.update()

    def insert(self, letter):
        o = self.text
        self.text = self.text[:self.cursor] + letter + self.text[self.cursor:]
        if o != self.text:
            self.cursor += 1
            self.cursor = np.clip(self.cursor, 0, len(self.text))

        self.update()

    def delete(self):
        if self.cursor != 0:
            self.text = self.text[:self.cursor - 1] + self.text[self.cursor:]
            self.cursor -= 1
            self.cursor = np.clip(self.cursor, 0, len(self.text))

    def receive_event(self, e):
        if e.type == pygame.KEYDOWN:
            if self.is_editing:
                if e.key == pygame.K_LEFT:
                    self.cursor -= 1
                    self.cursor = np.clip(self.cursor, 0, len(self.text))
                elif e.key == pygame.K_RIGHT:
                    self.cursor += 1
                    self.cursor = np.clip(self.cursor, 0, len(self.text))
                elif pygame.key.get_pressed()[pygame.K_LCTRL] and pygame.key.get_pressed()[pygame.K_a]:
                    self.text = ''
                    self.cursor = 0
                    self.update()
                else:
                    if e.key == pygame.K_BACKSPACE:
                        self.delete()
                        self.update()
                    elif e.key == pygame.K_RETURN:
                        if self.text != '':         # If text is blank we won't ever be able to edit it again
                            self.lost_focus()
                    else:
                        self.insert(e.unicode)
                        self.update()

    def click(self, mouse_pos):
        c = pygame.rect.Rect([int(self.pos[0]), int(self.pos[1] + self.padding[0]/2), int(self.text_rect[2]), int(self.text_rect[3] + self.padding[0])]).collidepoint(mouse_pos)

        return c

    def on_hover(self):
        self.color = [self.original_color[0] - 50, self.original_color[1] - 50, self.original_color[2] - 50]

        self.update()

    def on_click(self):
        self.is_editing = True

    def lost_focus(self):
        self.is_editing = False

    def update(self):
        self.font.size = 12 * self.scale
        self.display_text = self.font.render(self.text, self.color)[0]
        self.text_rect = self.display_text.get_rect()

        self.padding = self.original_padding * self.scale

def add(elements, obj):
    elements.append(obj)

def rRect(surface,rect,color,radius=.8):

    """
    AAfilledRoundedRect(surface,rect,color,radius=0.4)

    surface : destination
    rect    : rectangle
    color   : rgb or rgba
    radius  : 0 <= radius <= 1
    """

    rect         = pygame.rect.Rect(rect)
    color        = pygame.color.Color(*color)
    alpha        = color.a
    color.a      = 0
    pos          = rect.topleft
    rect.topleft = 0,0
    rectangle    = pygame.surface.Surface(rect.size,SRCALPHA)

    circle       = pygame.surface.Surface([min(rect.size)*3]*2,SRCALPHA)
    pygame.draw.ellipse(circle,(0,0,0),circle.get_rect(),0)
    circle       = pygame.transform.smoothscale(circle,[int(min(rect.size)*radius)]*2)

    radius              = rectangle.blit(circle,(0,0))
    radius.bottomright  = rect.bottomright
    rectangle.blit(circle,radius)
    radius.topright     = rect.topright
    rectangle.blit(circle,radius)
    radius.bottomleft   = rect.bottomleft
    rectangle.blit(circle,radius)

    rectangle.fill((0,0,0),rect.inflate(-radius.w,0))
    rectangle.fill((0,0,0),rect.inflate(0,-radius.h))

    rectangle.fill(color,special_flags=BLEND_RGBA_MAX)
    rectangle.fill((255,255,255,alpha),special_flags=BLEND_RGBA_MIN)

    return surface.blit(rectangle,pos)

def aaCircle(surface, color, pos, radius, filled = True):
    if filled:
        pygame.gfxdraw.filled_circle(surface, int(pos[0]), int(pos[1]), int(radius), color)
    pygame.gfxdraw.aacircle(surface, int(pos[0]), int(pos[1]), int(radius), color)
