import pygame 
from pygame.locals import *
import pygame.freetype as font

import pygame.cursors
import ast

import node 
from node import Node
from collections import OrderedDict
import pygame.gfxdraw
import copy
import numpy as np

import time

import os

import compile

font.init()
pygame.init()

edit = (               #sized 8x16
  "XXXXXXX ",
  "   X    ",
  "   X    ",
  "   X    ",
  "   X    ",
  "   X    ",
  "   X    ",
  "   X    ",
  "   X    ",
  "   X    ",
  "   X    ",
  "   X    ",
  "XXXXXXX ",
  "        ",
  "        ",
  "        ")

cursor, mask = pygame.cursors.compile(edit, "X", ".")   
edit = ((8, 16), (0, 0), cursor, mask)        

SCALE = 0.5
scale = 1

fonts = {'calibri':font.SysFont('arial', 30 * SCALE), 'calibri20':font.SysFont('arial', 25 * SCALE)}

def rRect(surface,rect,color,radius=0.4):
    
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
    circle       = pygame.transform.smoothSCALE(circle,[int(min(rect.size)*radius)]*2)

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

def distance(p1, p2):
    return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

def aaCircle(surface, color, pos, radius):
    pygame.gfxdraw.filled_circle(surface, int(pos[0]), int(pos[1]), int(radius), color)
    pygame.gfxdraw.aacircle(surface, int(pos[0]), int(pos[1]), int(radius), color)

import ctypes


res = pygame.display.list_modes()[1]
screen = pygame.display.set_mode([res[0], res[1]])

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

class Point:
    def __init__(self, coordinate):
        self.coordinate = coordinate

    def __getitem__(self, idx):
        return self.coordinate[idx]

class Box:
    def __init__(self, text, surface,name = "", pos = [0, 0], color = (255, 100, 100), text_color = (0, 0, 0), size = 10, font = 'calibri', node = None, has_params = False, text_boxes_ = []):
        self.font = fonts[font]
        self.orig_text = text
        self.text_color = text_color

        self.text = self.font.render(text, text_color)[0]
        self.name = textBox(form = "", font = 'calibri20', pos = [0, 0])
        self.name.add(name)
        
        self.text_width, self.text_height = self.text.get_rect().width, self.text.get_rect().height 

        self.width = self.text_width + 32 * SCALE   # 5 pixels of border on either side 
        self.orig_width = self.width

        self.height = 13 + 40 * SCALE # 5 pixels of border on either side 
        
        self.default_color = color 
        self.color = color

        self.pos = pos
        self.surface = surface

        self.rect = pygame.rect.Rect(self.pos[0], self.pos[1], self.width, self.height)
        self.is_selected = False 

        self.node = node

        self.delete_color = [100, 100, 100]
        self.has_params = has_params
        self.connection_points = OrderedDict()
        self.connection_points[Point([self.pos[0] + self.width/2, self.pos[1] - 14 * SCALE])] = None

        self.text_boxes = []

        for i in range (len(text_boxes_)):
            self.text_boxes.append(textBox(form = text_boxes_[i], form_color = (0, 0, 0), pos = [100, np.random.randint(0, 100)]))
            print text_boxes_[i]
        for i in range (len(text_boxes_)):
            self.text_boxes[i].pos[0] = self.pos[0] - 200 - 5 
            self.text_boxes[i].pos[1] = -10 + self.pos[1] + self.height + i * (self.height + 5)
            #self.text_boxes[i].rect = 

        self.is_editing = False

        if self.text_boxes != []:
            self.info_height = len(text_boxes_) * (self.text_boxes[0].height + 5) + 10
        else:
            self.info_height = 0
        self.info_width = 200

        self.info_rect = pygame.rect.Rect(self.pos[0] - 200 - 5, self.pos[1] + self.height + 5, self.info_width, self.info_height)

    def draw(self, sample = False):
        self.info_width = 250

        if self.is_selected: 
            rRect(self.surface, (self.rect[0] - 3, self.rect[1] - 3, self.rect[2] + 6, self.rect[3] + 6), color = (220, 50, 50, 100))

        self.name.pos = [self.pos[0] + 16 * SCALE + self.text_width, self.pos[1] + 20 * SCALE]
        self.name.rect = pygame.rect.Rect(self.name.pos[0], self.name.pos[1] - 10, self.name.width + 50, self.name.height + 20)
        self.rect = pygame.rect.Rect(self.pos[0], self.pos[1], self.width, self.height)
        rRect(self.surface, self.rect, self.color, radius = 0.4)
        screen.blit(self.text, (self.pos[0] + 16* SCALE, self.pos[1] + 20* SCALE))
        self.name.draw()
        
        keys = self.connection_points.keys()
        for p in range(len(keys)):
            #print p, [self.pos[0] + self.width/2, self.pos[1] - 14]
            if self.name.width != 2:
                if keys[p].coordinate == [self.pos[0] + self.width/2, self.pos[1] - 14 * SCALE]:
                    keys[p].coordinate = [self.pos[0] + (self.orig_width + self.name.width + 5)/2, self.pos[1] - 14 * SCALE] 
            else:
                if keys[p].coordinate == [self.pos[0] + self.width/2, self.pos[1] - 14 * SCALE]:
                    keys[p].coordinate = [self.pos[0] + (self.orig_width + self.name.width)/2, self.pos[1] - 14 * SCALE] 

        #print self.name.width 
        if self.name.width != 2:
            self.width = self.orig_width + self.name.width + 5
        else:
            self.width = self.orig_width + self.name.width

        if sample:
            aaCircle(self.surface, self.delete_color, [self.pos[0] + self.width + 2, self.pos[1] - 2], 6 * SCALE)
    
            keys = self.connection_points.keys()
            for p in range (len(keys)):
                pygame.draw.aaline(self.surface, (10, 10, 10), (self.pos[0] + self.width/2 - 1, self.pos[1]), (keys[p].coordinate[0] - 1, int(keys[p].coordinate[1])))

                if self.connection_points[keys[p]] != None:
                    aaCircle(screen, (150, 50, 50), [keys[p][0], keys[p][1]], 6* SCALE)
                else:
                    aaCircle(screen, (50, 155, 50), [keys[p][0], keys[p][1]], 6 * SCALE)
        
        for i in range (len(self.text_boxes)):
            self.text_boxes[i].pos[0] = self.pos[0] + 10
            self.text_boxes[i].pos[1] = 10 + self.pos[1] + self.height + 5 + i * (self.text_boxes[i].height + 5)
            #print self.text_boxes[i].pos
            self.text_boxes[i].rect = pygame.rect.Rect(self.text_boxes[i].pos[0], self.text_boxes[i].pos[1] - 10, self.text_boxes[i].width + 50, self.text_boxes[i].height + 20)
            
            if self.text_boxes[i].width + 60 > self.info_width:
                self.info_width = self.text_boxes[i].width + 70

            #print self.text_boxes[0].pos, self.text_boxes[1].pos

        self.info_rect = pygame.rect.Rect((self.pos[0], self.pos[1] + self.height + 5), (self.info_width, self.info_height))

    def drawText(self):
        if self.is_editing: 
            #self.info_rect = pygame.rect.Rect((self.pos[0] + self.width + 5, self.pos[1] + self.height + 5), (self.info_width, self.info_height))

            rRect(self.surface, self.info_rect, color = (220, 220, 220, 100), radius = 0.2)
            for t in self.text_boxes:
                t.draw()

    def isIn(self, pos = None):
        if pos == None:
            point = pygame.mouse.get_pos()
        else:
            point = pos
        return self.rect.collidepoint(point[0], point[1]) 
    
    def isInDelete(self):
        point = pygame.mouse.get_pos()
        return distance(point, [self.pos[0] + self.width + 2, self.pos[1] - 2]) <= 5
    
    def reposition(self, pos):
        non_orig = False 

        keys = self.connection_points.keys()
        for p in range(len(keys)):
            #print p, [self.pos[0] + self.width/2, self.pos[1] - 14]
            if keys[p].coordinate == [self.pos[0] + self.width/2, self.pos[1] - 14 * SCALE]:
                keys[p].coordinate = [pos[0] + self.width/2, pos[1] - 14 * SCALE] 
                non_orig = True 
        
        if not non_orig: 
            self.connection_points[Point([self.pos[0] + self.width/2, self.pos[1] - 14 * SCALE])] = None

        self.pos = pos
        self.rect = pygame.rect.Rect(self.pos[0], self.pos[1], self.width, self.height)
        

class textBox:
    def __init__(self, form, font = 'calibri', pos = [0, 0], form_color = (0, 0, 0)):
        if font == 'calibri':
            self.font = fonts['calibri20']
        elif font == 'calibri20':
            self.font = fonts['calibri']
        self.orig_form = form 
        self.form_color = form_color 
        self.form = self.font.render(form, self.form_color)[0]

        self.form_width, self.form_height = self.form.get_rect().width, self.form.get_rect().height
        self.width = self.form_width 
        self.height = 25 * SCALE

        print self.form.get_rect().width

        self.pos = pos
        self.response_t = ""
        self.response = self.font.render(self.response_t, form_color)[0]

        self.rect = pygame.rect.Rect(self.pos[0], self.pos[1] - 10, self.width  + 50, self.height + 20)
        self.response_width, self.response_height = self.response.get_rect().width, self.response.get_rect().height 

        self.is_editing = False 

    def add(self, text):
        self.response_t += text 
        self.response = self.font.render(self.response_t, self.form_color)[0]
        self.response_width, self.response_height = self.response.get_rect().width, self.response.get_rect().height 
        self.width = self.form_width + self.response_width 
        #self.height = self.response_height 

        self.rect = pygame.rect.Rect(self.pos[0], self.pos[1] - 10, self.width + 50, self.height + 20)
    def isIn(self, pos = None):
        if pos == None:
            point = pygame.mouse.get_pos()
        else:
            point = pos
        return self.rect.collidepoint(point[0], point[1]) 
    def delete(self):
        self.response_t = self.response_t[:-1] 
        self.response = self.font.render(self.response_t, self.form_color)[0]
        self.response_width, self.response_height = self.response.get_rect().width, self.response.get_rect().height 
        self.width = self.form_width + self.response_width 
        #self.height = self.response_height 

        self.rect = pygame.rect.Rect(self.pos[0], self.pos[1] - 10, self.width+ 50, self.height + 20)

    def draw(self):
        #print self.form
        if self.is_editing: 
            if self.response_width < 40:
                pygame.draw.rect(screen, (254, 255, 255), (self.pos[0] + self.form_width, self.pos[1] - 2,  50, self.height + 4))
            else:
                pygame.draw.rect(screen, (254, 255, 255), (self.pos[0] + self.form_width, self.pos[1] - 2,  self.response_width + 10, self.height + 4))


        screen.blit(self.form, self.pos)
        #print self.pos
        screen.blit(self.response, (self.pos[0] + self.form_width + 5, self.pos[1]))

def build_tree(nodes, boxes):
    try:
        for n in nodes:
            # Flush everything so you don't expand the tree by accident 
            n.parents = [None]
            n.children = []

        target_idx = 0
        root_idx = 0
        for i in range (len(nodes)):
            if nodes[i].type == 'INPUT':
                root_idx = i
            if nodes[i].type == 'target':
                target_idx = i

        root = boxes[root_idx]
        queue = Queue()

        queue.add(root)
        root_node = nodes[root_idx]

        steps = 0

        while not queue.isEmpty():
            steps += 1
            if steps > 10000:
                print "Can't build tree! "
                return "Can't build tree! "

            box = queue.pop()
            for b in range(len(boxes)):
                if boxes[b] == box:
                    box_idx = b

            node = nodes[box_idx]
            
            # Search for all layers that have "node" as a connection"
            connection_nodes = []
            for box_ in boxes:
                if box_ in box.connection_points.values():
                    #print "appdending"
                    queue.add(box_)
                    
                    for b in range(len(boxes)):
                        if boxes[b] == box_:
                            idx = b

                    #print box_.has_params
                    if boxes[idx].has_params:
                        #print boxes[idx + 1].text
                        queue.add(boxes[idx + 1])

                    if boxes[idx].has_params:
                        if nodes[idx].parents[0] == None:
                            nodes[idx].parents[0] = node.name
                            nodes[idx + 1].parents[0] = node.name 
                        else:
                            nodes[idx].parents.append(node.name)
                            nodes[idx + 1].parents.append(node.name)
                        
                        node.children.append(nodes[idx + 1])
                        node.children.append(nodes[idx])

                    else:
                        if nodes[idx].parents[0] == None:
                            nodes[idx].parents[0] = node.name
                        else:
                            nodes[idx].parents.append(node.name)
                            print nodes[idx].parents
                        
                        node.children.append(nodes[idx])

                    if node.type == 'INPUT':
                            queue.add(boxes[target_idx])
                            node.children.append(nodes[target_idx])

                    #print node.type + " is appending " + nodes[idx].type + " type"
            
        queue = Queue()
        queue.add(root_node)

        while not queue.isEmpty():
            node = queue.pop() 
            print node.type 

            for i in node.children: 
                queue.add(i)

        return root_node   
    except: 
        return "404 Error, Webpage not found"

def main():
    cont = True
    #modes = pygame.display.list_modes(16)
    #print modes
    #screen = pygame.display.set_mode(modes[0], FULLSCREEN, 16)
    #sample_conv = Box(text = "input", surface = screen, pos = [])
    sample_conv = Box(text = "convolution", surface = screen, pos = [5, 20])
    sample_fc =  Box(text = "matmul", surface = screen, pos = [5, sample_conv.height + 30])
    sample_relu = Box(text = "ReLU", surface = screen, pos = [5, sample_conv.height + sample_fc.height + 40], color = (150, 200, 200))
    sample_sigmoid = Box(text = "sigmoid", surface = screen, pos = [5, sample_conv.height + sample_fc.height + sample_relu.height + 50], color = (150, 200, 200))
    sample_loss = Box(text = "mse_loss", surface = screen, pos = [5, sample_conv.height + sample_fc.height + sample_relu.height + sample_sigmoid.height + 60], color = (200, 200, 150))
    sample_grad = Box(text = "grad", surface = screen, pos = [5, sample_conv.height + sample_fc.height + sample_relu.height + sample_sigmoid.height + sample_loss.height + 70], color = (150, 150, 150))
    sample_flatten = Box(text = "flatten", surface = screen, pos = [5, sample_conv.height + sample_fc.height + sample_relu.height + sample_sigmoid.height + sample_loss.height + sample_grad.height + 80], color = (150, 150, 150))
    sample_output = Box(text = "output", surface = screen, pos = [5, sample_conv.height + sample_fc.height + sample_relu.height + sample_sigmoid.height + sample_loss.height + sample_grad.height +sample_flatten.height + 90], color = (150, 150, 150))
    sample_target = Box(text = "target", surface = screen, pos = [5, sample_conv.height + sample_fc.height + sample_relu.height + sample_sigmoid.height + sample_loss.height + sample_grad.height +sample_flatten.height + sample_output.height + 100], color = (200, 150, 200))
    sample_input = Box(text = "input", surface = screen, pos = [5 ,  sample_conv.height + sample_fc.height + sample_relu.height + sample_sigmoid.height + sample_loss.height + sample_grad.height +sample_flatten.height + sample_output.height + sample_target.height + 110], color = (200, 150, 200))
    sample_merge = Box(text = "merge", surface = screen, pos = [5, sample_input.pos[1] + sample_input.height + 10], color = (255, 180, 100))
    sample_split = Box(text = "split", surface = screen, pos = [5, sample_merge.pos[1] + sample_merge.height + 10], color = (255, 180, 100))
    #sample_substitute = Box(text = "substitute", surface = screen, pos = [5, sample_split.height + sample_split.pos[1] + 10], color = )

    #sample_pooling = Box(text = "pool", surface = screen, pos = [5, sample_conv.height + sample_fc.height + sample_relu.height + sample_sigmoid.height + sample_input.height + sample_loss.height + sample_grad.height +sample_flatten.height + sample_target.height + 110], color = (150, 150, 150))

    samples = [sample_conv, sample_fc, sample_relu, sample_sigmoid, sample_input, sample_loss, sample_grad, sample_flatten, sample_target, sample_output, sample_merge, sample_split]

    meta_text_boxes = []

    def add(text, textBox):
        textBox.rect = pygame.rect.Rect(textBox.pos[0], textBox.pos[1] - 10, textBox.width  + 50, textBox.height + 12)

        text.append(textBox)

    text_boxes = []
    add(text_boxes, textBox(form = "output maps: ", form_color = (100, 100, 100)))

    meta_text_boxes.append(["output maps: ", "input maps: ", "filter height: ", "filter width: ", "subsample width: ", "subsample height: "])
    meta_text_boxes.append(["input size: ", "output size: "])
    meta_text_boxes.append(["merge axis: "])
    meta_text_boxes.append(["split axes: "])

    text_boxes=[]

    nodes = []
    boxes = []

    layers = 0

    is_click = False 
    is_editing = False 
    is_dragging = False
    is_dragging_board = False 
    is_focused = False 
    is_in = False 
    is_doubleclick = False 
    is_selecting = False
    orig_pos = [0, 0]

    selected = []

    c = 0

    click_time = 0

    offset_x, offset_y = 0,0
    while cont:
        c += 1

        active_text_boxes = []

        boxes_to_delete = []

        for event in pygame.event.get():
            if event.type == QUIT:
                cont = False 
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                is_editing = False
                #is_dragging = True 
                is_click = True
                if time.time() - click_time < 0.5:      # If the user has clicked twice within 0.5 seconds
                    is_doubleclick = True
                else:
                    is_doubleclick = False
                click_time = time.time()

                if pygame.mouse.get_pressed()[0]:
                    if screen.get_at(pygame.mouse.get_pos()) == (255, 255, 255, 255): 
                        for box in selected:
                            box.is_selected = False

                        selected = []
                        
                    if screen.get_at(pygame.mouse.get_pos()) == (255, 255, 255, 255): 

                        is_selecting = pygame.rect.Rect(list(pygame.mouse.get_pos()), [1, 1])
                        is_focused = False
                else:
                    is_dragging_board = True

                    pygame.mouse.get_rel() 

            elif event.type == pygame.MOUSEBUTTONUP:
                is_dragging_board = False 
                is_selecting = False

                if type(is_dragging) == list and is_in and is_in != is_dragging[0]:
                    k = is_dragging[0].connection_points.keys()[is_dragging[1]]
                    is_dragging[0].connection_points[k] = is_in

                    oldkey, newkey = k, Point([is_in.pos[0] + is_in.width/2, is_in.pos[1] + is_in.height + 8])

                    is_dragging[0].connection_points = OrderedDict((newkey if k == oldkey else k, v) for k, v in is_dragging[0].connection_points.viewitems())

                is_dragging = False
                is_click = False 
                is_in = False 
            
            elif event.type == pygame.KEYDOWN:
                if is_editing != False:
                    
                    if event.key == pygame.K_ESCAPE:
                        os.system('cls')
                        print "compiling..."
                        comp = compile.compile_graph(4, 2, build_tree(nodes, boxes))
                        if comp == 0:
                            print "compile successful!"
                        else:
                            print comp

                    if event.key == pygame.K_BACKSPACE:
                        is_editing.delete()
                    else:
                        if event.key != pygame.K_RETURN:
                            
                            try:
                                is_editing.add(event.unicode)
                            except ValueError:
                                pass

                elif event.key == pygame.K_ESCAPE:
                    os.system('cls')

                    print "compiling"
                    comp = compile.compile_graph(4, 2, build_tree(nodes, boxes))
                    if comp == 0:
                        print "compile successful!"
                    else:
                        print comp

        # Put screenfill here because it might mess up with some color detection 
        screen.fill((255, 255, 255))

        if is_dragging_board:
            rel = pygame.mouse.get_rel()
            for box in boxes:
                box.reposition([box.pos[0] + rel[0], box.pos[1] + rel[1]])

        if is_selecting != False:
            mp = pygame.mouse.get_pos()
            is_selecting = pygame.rect.Rect(is_selecting[0], is_selecting[1], mp[0] - is_selecting[0], mp[1] - is_selecting[1])
            pygame.draw.rect(screen, (240, 240, 240, 100), is_selecting)

        for sample in samples:
            sample.draw()
            
            if sample.isIn():
                sample.color = [sample.default_color[0] - 50, sample.default_color[1] - 50, sample.default_color[2] - 50]
                if pygame.mouse.get_pressed()[0] and is_click:
                    if sample.orig_text == "convolution":
                        nodes.append(Node(name = 'conv' + str(layers), parent = "inp", type = "conv", mode = "half", param_size = [1, 1, 1, 1], subsample_x = 1, subsample_y = 1))
                        boxes.append(Box(text = "convolution / " ,  surface = screen,name = nodes[-1].name, pos = sample.pos, color = sample.default_color, has_params = True, text_boxes_ = meta_text_boxes[0]))
                        print len(nodes) 
                        layers += 1
                        nodes.append(Node(name = 'param' + str(layers), type = 'param', param_size = nodes[-1].param_size))
                        boxes.append(Box(text = 'param / ' , surface = screen, name = nodes[-1].name, pos = [sample.pos[0] + boxes[-1].width + 2, sample.pos[1]], color = (100, 100, 100)))

                        layers += 1
                    elif sample.orig_text == "matmul":
                        nodes.append(Node(name = 'dot' + str(layers), type = "matmul", param_size = [1, 1]))
                        boxes.append(Box(text = "matmul / " , surface = screen, name =  nodes[-1].name, pos = sample.pos, color = sample.default_color, has_params = True, text_boxes_ = meta_text_boxes[1]))
                        print len(nodes) 
                        layers += 1
                        nodes.append(Node(name = 'param' + str(layers), type = 'param', param_size = nodes[-1].param_size))
                        boxes.append(Box(text = 'param / ' , surface = screen, name = nodes[-1].name, pos = [sample.pos[0] + boxes[-1].width + 2, sample.pos[1]], color = (100, 100, 100)))

                        layers += 1
                    elif sample.orig_text == "ReLU":
                        nodes.append(Node(name = 'relu' + str(layers), type = "relu"))
                        boxes.append(Box(text = "ReLU / " , surface = screen, name = nodes[-1].name, pos = sample.pos, color = sample.default_color))
                        print len(nodes) 
                        layers += 1
                    elif sample.orig_text == "sigmoid":
                        nodes.append(Node(name = 'sigmoid' + str(layers), type = "sigmoid"))
                        boxes.append(Box(text = "sigmoid / " , surface = screen, name = nodes[-1].name, pos = sample.pos, color = sample.default_color))
                        print len(nodes) 
                        layers += 1
                    elif sample.orig_text == "input":
                        nodes.append(Node(name = 'inp' + str(layers), type = "INPUT"))
                        boxes.append(Box(text = "input / " , surface = screen, name = nodes[-1].name, pos = sample.pos, color = sample.default_color))
                        print len(nodes) 
                        layers += 1
                    elif sample.orig_text == "mse_loss":
                        nodes.append(Node(name = 'loss' + str(layers), type = 'mse_loss'))
                        boxes.append(Box(text = 'mse_loss / ', surface = screen,name = nodes[-1].name,  pos = sample.pos, color = sample.default_color))
                        layers += 1
                    elif sample.orig_text == "grad":
                        nodes.append(Node(name = 'grad' + str(layers), type = "gradient"))
                        boxes.append(Box(text = 'grad / ', surface = screen, name = nodes[-1].name, pos = sample.pos, color = sample.default_color))
                        layers += 1
                    
                    elif sample.orig_text == 'flatten':
                        nodes.append(Node(name = 'flat' + str(layers), type = 'flatten'))
                        boxes.append(Box(text = 'flatten / ', surface = screen, name = nodes[-1].name, pos = sample.pos, color = sample.default_color))
                        layers += 1
                    elif sample.orig_text == 'target':
                        nodes.append(Node(name = 'target' + str(layers), type = 'target'))
                        boxes.append(Box(text = 'target / ', surface = screen, name = nodes[-1].name, pos = sample.pos, color = sample.default_color))
                        layers += 1
                    elif sample.orig_text == "output":
                        nodes.append(Node(name = 'out' + str(layers), type = 'output'))
                        boxes.append(Box(text = 'output / ' , surface = screen,name = nodes[-1].name, pos = sample.pos, color = sample.default_color))
                        layers += 1
                    
                    elif sample.orig_text == "merge":
                        nodes.append(Node(name = 'merge' + str(layers), type = 'merge', param_size = [-1]))
                        boxes.append(Box(text = 'merge / ' , surface = screen, name = nodes[-1].name, pos = sample.pos, color = sample.default_color, text_boxes_ = meta_text_boxes[2]))
                    elif sample.orig_text == "split":
                        nodes.append(Node(name = "split" + str(layers), type = 'split', param_size = '[:]'))
                        boxes.append(Box(text = "split / ", surface = screen, name = nodes[-1].name, pos = sample.pos, color = sample.default_color, text_boxes_ = meta_text_boxes[3]))

                    if len(boxes) > 1:
                        if boxes[-2].has_params:
                            is_dragging = boxes[-2]
                        else:
                            is_dragging = boxes[-1]
                    else:
                        is_dragging = boxes[-1]
                    is_click = False
            else:
                sample.color = sample.default_color
        
        is_in = False
        in_text = False 

        for box in boxes:
            if "param" in box.orig_text:
                idx = boxes.index(box) - 1

                box.reposition([boxes[idx].pos[0] + boxes[idx].rect[2] + 2, boxes[idx].pos[1]])

            if box.is_editing:  # if it's true, then don't check for doubleclick
                if is_focused == box: 
                    box.is_editing = True 
                else:
                    box.is_editing = False
            else:
                if is_focused == box and is_doubleclick: 
                    box.is_editing = True 
                else:
                    box.is_editing = False

            box.draw(sample = True)
            
        for box in boxes:
            if box.is_editing:
                box.drawText()
            if is_selecting:
                if is_selecting.collidepoint(box.pos[0], box.pos[1]):
                    box.is_selected = True 
                    if box not in selected:
                        selected.append(box)
                        print selected
        
        if not is_selecting:
            for box in boxes:
                if box.isIn():
                    is_in = box 

                    box.color = [box.default_color[0] - 50, box.default_color[1] - 50, box.default_color[2] - 50]
                # print screen.get_at(pygame.mouse.get_pos())
                    if pygame.mouse.get_pressed()[0] and is_click and list(screen.get_at(pygame.mouse.get_pos())) == box.color + [255] and is_selecting: 
                        # We just dragged everything that is selected 
                        orig_pos = pygame.mouse.get_pos()
                        pygame.mouse.get_rel()
                        is_dragging = box

                    if pygame.mouse.get_pressed()[0] and is_click and list(screen.get_at(pygame.mouse.get_pos())) == box.color + [255] and not is_selecting:
                        if  (not boxes[boxes.index(box) - 1].has_params):
                            is_dragging = box
                            offset_x, offset_y = is_dragging.pos[0] - pygame.mouse.get_pos()[0], is_dragging.pos[1] - pygame.mouse.get_pos()[1] 
                            offset_x = -offset_x 
                            offset_y = -offset_y

                            pygame.mouse.get_rel()

                        is_click = False
                        is_focused = box
                        

                        #box.delete_color
                        
                        #is_dragging[0].connection_points.keys()[is_dragging[1]]]
                    #  print is_dragging[0].connection_points

                elif box.isInDelete() and list(screen.get_at(pygame.mouse.get_pos())) != box.delete_color + [255]:

                    box.delete_color = [255, 10, 10]
                    box.color = box.default_color

                    if pygame.mouse.get_pressed()[0] and is_click:
                        boxes_to_delete = box, nodes[boxes.index(box)]

                else:
                    box.color = box.default_color
                    box.delete_color = [100, 100, 100]

                for p in range (len(box.connection_points.keys())):
                    mouse_pos = pygame.mouse.get_pos() 

                # print box.connection_points

                    if distance(mouse_pos, box.connection_points.keys()[p].coordinate) < 9 and is_click and list(screen.get_at(pygame.mouse.get_pos())) != [50, 155, 50, 255]:
                        is_dragging = [box, p]
                        is_focused = [box, p]
                        is_click = False 
                    
                    check = box.connection_points[box.connection_points.keys()[p]] 
                    
                    if type(is_dragging) == list:
                        if is_dragging[0].connection_points[is_dragging[0].connection_points.keys()[is_dragging[1]]] == check:    # If they're the same, then we disconnect them 
                            is_dragging[0].connection_points[is_dragging[0].connection_points.keys()[is_dragging[1]]] = None
                            check = None
                        
                        elif check != None:
                            oldkey, newkey = box.connection_points.keys()[p], Point([check.pos[0] + check.width/2, check.pos[1] + check.height + 8])
                            box.connection_points = OrderedDict((newkey if k == oldkey else k, v) for k, v in box.connection_points.viewitems())

                    else:
                        if check != None:
                            oldkey, newkey = box.connection_points.keys()[p], Point([check.pos[0] + check.width/2, check.pos[1] + check.height + 8])
                            box.connection_points = OrderedDict((newkey if k == oldkey else k, v) for k, v in box.connection_points.viewitems())
                        #if not check.isIn(box.connection_points.keys()[p].coordinate):  # If the point is not in the layer, we'll remove it as a connected layer
                    #        box.connection_points[box.connection_points.keys()[p]] = None 
                
                #        print box.connection_points[box.connection_points.keys()[p]] 
        
        #active_text_boxes = [item for sublist in active_text_boxes for item in sublist]
        for box in boxes:

            if not box.is_editing and is_click:
                for text in box.text_boxes + [box.name]:    # We (may have) lost focus of a text box
                    text.is_editing = False 

                    try:
                        idx = boxes.index(box)
                        if "output maps" in text.orig_form:
                            nodes[idx].param_size[0] = int(text.response_t)
                        elif "input maps" in text.orig_form:
                            nodes[idx].param_size[1] = int(text.response_t)
                        elif "filter width" in text.orig_form:
                            nodes[idx].param_size[2] = int(text.response_t)
                        elif "filter height" in text.orig_form:
                            nodes[idx].param_size[3] = int(text.response_t)
                        elif "input size" in text.orig_form or "merge axis" in text.orig_form:
                            nodes[idx].param_size[0] = int(text.response_t)
                        elif "output size" in text.orig_form:
                            nodes[idx].param_size[1] = int(text.response_t)
                        elif "subsample width" in text.orig_form:
                            nodes[idx].subsample_x = int(text.response_t)
                        elif "subsample height" in text.orig_form:
                            nodes[idx].subsample_y = int(text.response_t)
                        elif "split axes" in text.orig_form:
                            nodes[idx].param_size = str(text.response_t)
                        elif text.orig_form == "":
                            nodes[idx].name = str(text.response_t)
                    
                    except ValueError:
                        #print "passed", text.orig_form
                        pass 

            if box.is_editing:
                for text in box.text_boxes + [box.name]:
                    if text.isIn():
                        if is_click:
                            is_editing = text
                        pygame.mouse.set_cursor(*edit)
                        in_text = True 
                    
                    if is_editing == text:
                        text.is_editing = True 
                    else:
                        text.is_editing = False

                    
                            
                    #print text.rect
                    #text.draw()
        if not in_text:
            pygame.mouse.set_cursor(*pygame.cursors.arrow)
        #print active_text_boxes

        if is_dragging != False:
            


            if type(is_dragging) == list:       # We are dragging a connection point 
                is_dragging[0].connection_points.keys()[is_dragging[1]].coordinate = pygame.mouse.get_pos()

                non_orig = False 
                for p in range(len(is_dragging[0].connection_points.keys())):
                    if is_dragging[0].connection_points.keys()[p].coordinate == [is_dragging[0].pos[0] + is_dragging[0].width/2, is_dragging[0].pos[1] - 14 * SCALE]:
                        non_orig = True 
                
                if not non_orig:
                    is_dragging[0].connection_points[Point([is_dragging[0].pos[0] + is_dragging[0].width/2, is_dragging[0].pos[1] - 14 * SCALE])] = None

            else:
                if selected and is_dragging.is_selected:
                    is_dragging.reposition([pygame.mouse.get_pos()[0] - offset_x, pygame.mouse.get_pos()[1] - offset_y])

                    if is_dragging.has_params:
                        boxes[boxes.index(is_dragging) + 1].reposition([pygame.mouse.get_pos()[0] + is_dragging.width + 2 - offset_x, -offset_y + pygame.mouse.get_pos()[1]])

                    rel =pygame.mouse.get_rel()
                    for box_ in boxes:
                        box_.reposition([box_.pos[0] + rel[0], box_.pos[1] + rel[1]])

                is_dragging.reposition([pygame.mouse.get_pos()[0] - offset_x, pygame.mouse.get_pos()[1] - offset_y])

                if is_dragging.has_params:
                    boxes[boxes.index(is_dragging) + 1].reposition([pygame.mouse.get_pos()[0] + is_dragging.width + 2 - offset_x, -offset_y + pygame.mouse.get_pos()[1]])

        if c % 2 == 0:
            pygame.display.flip()

        if boxes_to_delete:
            idx = boxes.index(boxes_to_delete[0])

            # Find any references to this layer and set them to none. Safely exiting essentially
            for box in boxes:
                try:
                    dict_idx = box.connection_points.values().index(boxes_to_delete[0]) 
                    box.connection_points[box.connection_points.keys()[dict_idx]] = None
                except ValueError:
                    pass

            # Actually delete the damn things
            del boxes[idx]
            del nodes[idx]
        

            
main()
