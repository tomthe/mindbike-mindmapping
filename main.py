# -*- coding: utf-8 -*-

# MindBike Mindmapping - Mindmap viewer and editor for mobile devices and desktop platforms
# Copyright (C) 2014 Tom Theile
# This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 3 of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this program; if not, see <http://www.gnu.org/licenses/>.

__version__ = "0.3"

import kivy
from kivy.app import App
#from kivy.config import Config
from kivy.uix.modalview import ModalView
from kivy.uix.boxlayout import BoxLayout
#from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.dropdown import DropDown
from kivy.properties import ListProperty, StringProperty,ObjectProperty, BooleanProperty
from kivy.uix.popup import Popup
from kivy.logger import Logger
from kivy.core.window import Window
from random import randint
from time import time
from shutil import copyfile
try:
    from copy import deepcopy
    Logger.info("successfully imported deepcopy")
except ImportError,e:
    Logger.Error("couldn't load 'deepcopy'" + e)
#from readmm import stringize

try:
  from lxml import etree
  Logger.info("running with lxml.etree")
except ImportError:
  try:
    # Python 2.5
    import xml.etree.cElementTree as etree
    Logger.info("running with cElementTree on Python 2.5+")
  except ImportError:
    try:
      # Python 2.5
      import xml.etree.ElementTree as etree
      Logger.info("running with ElementTree on Python 2.5+")
    except ImportError:
      try:
        # normal cElementTree install
        import cElementTree as etree
        Logger.info("running with cElementTree")
      except ImportError:
        try:
          # normal ElementTree install
          import elementtree.ElementTree as etree
          Logger.info("running with ElementTree")
        except ImportError:
          Logger.Error("Failed to import ElementTree from any known place")


kivy.require('1.0.7')


MIN_NODE_WIDTH = 30
MAX_NODE_WIDTH = 400



class NodeTextInput(TextInput):
    node=None

    def __init__(self,**kwargs):
        #print "node kwargs:", kwargs
        self.size_hint = (None,None)
        self.node=kwargs['node']
        self.node.rootwidget.textinput_is_active = True
        #self.bind(focus=self.on_focus)
        super(NodeTextInput, self).__init__(**kwargs)

    def on_text_validate(self,remove_enter=False):
        if remove_enter:
            self.text = self.text[:-1]
        #print "on_text_validate1-1", self.node.text, "|||",self.text
        newtext=self.text
        self.node.text=unicode(newtext,'utf-8')
        self.node.rootwidget.textinput_is_active = False
        #self.node.rootwidget.textinput  = None
        if self.parent:
            self.parent.remove_widget(self)
        else:
            Logger.warning("no parent available")
        self.focus=False
        self.node.on_text2()
        self.node.rootwidget.rebuild_map()

    def on_focus(self,instance,value):
        if value:
            pass
        else:
            self.on_text_validate()
        return super(NodeTextInput, self).on_focus(instance,value)

    #def on_enter(self,instance,value):
    #    print "enter gedrueckt!!"
    #   pass

    def on_text(self,instance,value):
        #print "line numbers: ", value.count('\n')
        #self.height = (1 + value.count('\n')) * 22
        self.adjust_input_size()

    def adjust_input_size(self):
        #print "line_height:", self.line_height, self.font_size,self.font_name, self.minimum_height, ", (self.t...): ", (2 + self.text.count('\n')) * (self.font_size + 3)
        self.height = max(self.minimum_height, (2 + self.text.count('\n')) * (self.font_size + 3))#(1 + self.text.count('\n')) * 19 + 10
        #print "line_heigh2:", self.line_height, self.font_size,self.font_name, self.height
        self.width = 400

class Node(Label):
    selected=BooleanProperty(False)
    ntext = StringProperty()
    folded = False
    bbox=[100,15]
    nid=""
    #childnodes = ListProperty([])
    nodetextlabel = ObjectProperty()
    xmlnode = None
    bgcolor = ListProperty([1,1,1])
    color = ListProperty([0,0.03,0.01,1])#[0,0.2,1.0,1] #
    #posright = AliasProperty(get_posright, set_posright, bind=('pos', 'width'))
    fathers_end_pos=[0,33]
    fathers_width=20
    father_node=None
    child_nodes = []
    siblings = []
    VERTICAL_MARGIN = 5

    def on_selected(self,instance,value):
        #self.rootwidget.deselect_all()
        if value:
            self.bgcolor = [0.80,0.90,0.90]
            self.rootwidget.selectedNodeID=self.xmlnode.get("ID")
            self.rootwidget.selectedNode=self
            #print self.pos, self.parent.size,self.parent.parent.size, self.parent.parent.scroll_x,self.parent.parent.scroll_y
            self.get_optimal_scroll_pos()
        else:
            self.bgcolor = [1,1,1]

    def get_optimal_scroll_pos(self):
        #vertical:
        try:
            bottom_bound = self.parent.parent.scroll_y * (self.parent.height-self.parent.parent.height)
            upper_bound = bottom_bound + self.parent.parent.height
            if self.y >= upper_bound:
                self.parent.parent.scroll_y = (float(self.y)/self.parent.height)
            elif self.y <= bottom_bound:
                self.parent.parent.scroll_y = (float(self.y)/self.parent.height)
            #horizontal:

            left_bound = self.parent.parent.scroll_x * (self.parent.width-self.parent.parent.width)
            right_bound = left_bound + self.parent.parent.width
            if self.x >= right_bound:
                self.parent.parent.scroll_x = (float(self.x)/self.parent.width)
            elif self.x <= left_bound:
                self.parent.parent.scroll_x = (float(self.x)/self.parent.width)
        except Exception, e:
            Logger.error("get_optimal_scroll_pos..." + str(e))

    def set_posright(self,value):
        self.pos= [value[0] - self.width, value[1]]

    def get_posright(self):
        return [self.x + self.width,self.y]

    def on_touch_down(self, touch):
        self.selected =False
        if self.collide_point(*touch.pos):
            if touch.is_double_tap:
                self.edit()
            else:
                self.selected = True
        return super(Node, self).on_touch_down(touch)

    def edit(self,text=""):
        self.rootwidget.textinput_is_active = True
        if self.text== "_":
            self.text=""
        textinput = NodeTextInput(node=self, pos=self.pos,text=self.text + text, focus=True, multiline=True)
        self.rootwidget.add_widget(textinput)
        #self.rootwidget.textinput = textinput


    def fold_unfold(self):
        #print "fold,unfold"
        if self.folded==False:
            self.fold()
        else:
            self.unfold()
        self.selected = True
        #self.rootwidget.selectedNode = self
        self.rootwidget.rebuild_map(do_for_undo=False)

    def fold(self):
        #print "fold:  ", self.text
        self.folded = True
        self.xmlnode.set("FOLDED","True")

    def unfold(self):
        self.folded = False
        self.xmlnode.set("FOLDED","False")
        self.create_itself(self.xmlnode,self.rootwidget,[self.x,self.y],unfold=True)

    def on_text2(self):
        if self.text[0]=="=":
            try:
                Logger.info("eval: " + str(self.text))
                self.text=str(eval(self.text[1:]))
            except Exception, e:
                Logger.error(str(e) + "; eval: " + str(self.text))
        #Seconds since epoch:
        modified = str(int(time()*1000))
        self.xmlnode.set("MODIFIED",modified)
        self.xmlnode.set(u"TEXT",unicode(self.text,))
        #self.rootwidget.rebuild_map()

    def add_sibling(self):
        n_siblings = len(self.siblings)
        #print ([x.tag for x in self.father_node.xmlnode])
        n_non_node_xmls = len([x.tag for x in self.father_node.xmlnode]) - n_siblings
        n_non_node_xmls_until_now = len([x.tag for x in self.father_node.xmlnode][self.i_sibling-1:]) - [x.tag for x in self.father_node.xmlnode][self.i_sibling-1:].count("node")
        #print "n_siblings:", n_siblings, " not-node-xmls: ", n_non_node_xmls, "; i_sibling: ", self.i_sibling, "; n_non_node_xmls_until_now: ", n_non_node_xmls_until_now
        position = len(self.siblings) - self.i_sibling + 1 + n_non_node_xmls_until_now
        #print "p, p2: ", position
        self.father_node.add_child(position)

    def add_child(self,position=200):
        #einen neuen "node" erstellen
        #<node TEXT="knot1-2" ID="ID_1021949625" CREATED="1400192771540" MODIFIED="1400197616894">
        #TEXT="nimi" ID="ID_1004240095" CREATED="140 062 763 512 6" MODIFIED="1400627638635"
        newxmlnode = etree.Element("node")
        #The Text is empty
        TEXT="_"
        #a random ID between 10E9 and 10E10:
        ID = "ID_"+ str(randint(1000000000,10000000000))
        self.nid=ID
        #Seconds since epoch:
        CREATED = str(int(time()*1000))
        #set the xml-node-Attributes:
        newxmlnode.set("TEXT",TEXT)
        newxmlnode.set("ID",ID)
        newxmlnode.set("CREATED",CREATED)
        newxmlnode.set("MODIFIED",CREATED)
        newxmlnode.set("SELECTED","TRUE")
        self.xmlnode.set("FOLDED","False")
        self.xmlnode.insert(position,newxmlnode)
        self.rootwidget.rebuild_map(do_for_undo=False)
        return ID

    def create_itself(self,xmlnode,rootwidget,pos,unfold=False,fathers_end_pos=[20,20],fathers_width=50, father_node=None,i_sibling=0):
        if xmlnode.tag=="node":

            #print "fathersendpos.pos, self.ext: (nnerhalb...,", self.fathers_end_pos,self.text, "fathers..."
            self.father_node = father_node
            self.child_nodes = []
            self.xmlnode = xmlnode
            self.rootwidget = rootwidget
            self.fathers_end_pos= fathers_end_pos
            self.fathers_width = fathers_width
            self.text = xmlnode.get("TEXT","NO_TEXT")
            if self.text == "":
                self.text = "_"

            self.nid = xmlnode.get("ID")
            self.texture_update()
            self.size = self.texture_size
            if self.width >= MAX_NODE_WIDTH:
                self.text_size = (MAX_NODE_WIDTH,None)
                self.texture_update()
                self.size = self.texture_size
            if self.width <=MIN_NODE_WIDTH:
                self.width = MIN_NODE_WIDTH
            #if self.width >=MAX_NODE_WIDTH:
            #    self.width = MAX_NODE_WIDTH

            self.bby = self.height + self.VERTICAL_MARGIN
            self.pos = pos
            self.i_sibling =i_sibling
            #print i_sibling, self.text
            i_sibling_for_children=0
            childpos=[pos[0]+self.size[0]+70,pos[1]]
            has_open_children = False
            if self.xmlnode.get("SELECTED","False")=="TRUE":
                self.selected=True
                del self.xmlnode.attrib["SELECTED"]
            if xmlnode.get("FOLDED")=="False" or unfold==True:
                xmlnode.set("FOLDED","False")
                self.folded=False
                for nodechild in reversed(xmlnode):
                    if nodechild.tag=="node":
                        i_sibling_for_children +=1
                        has_open_children=True
                        newnode = Node()
                        rootwidget.add_widget(newnode)
                        # newnode.canvas.
                        childboxy = newnode.create_itself(nodechild,rootwidget,childpos,fathers_end_pos= self.pos,fathers_width=self.width, father_node=self,i_sibling=i_sibling_for_children)#,color=self.color)

                        #self.childnodes.append(newnode)
                        childpos[1]  += childboxy
                        self.bby += childboxy
                        self.child_nodes.append(newnode)
                for childnode in self.child_nodes:
                    childnode.siblings = self.child_nodes

                if has_open_children:
                    if self.height < self.bby:
                        self.bby -= self.height + self.VERTICAL_MARGIN
                        self.pos[1] += self.bby/2 - self.height/2 #-4
                        if self.bby < self.height:
                            self.pos[1] -= self.bby/2 - self.height/2 #-4
                            self.bby = self.height
                    else:
                        self.bby = self.height
            else:
                self.folded = True
                if xmlnode.find("node") !=None:
                    #the node has folded kids
                    self.bgcolor = [1,0.97,0.91]
                    self.canvas.ask_update()
            #self.size = [self.nwidth,self.nheight]

            if self.right > self.rootwidget.width:
                self.rootwidget.width = self.right + 50
            return self.bby
        else:
            return 0

class MapView(RelativeLayout):
    rootnode=None
    firstnode=None
    tree = None
    loaded_map_filename = "test.mm"
    selectedNodeID="0"
    textinput_is_active = False
    mapview_is_active = False
    undostack = []
    undopos = -1
    bgcolor = ListProperty([1,1.0,1,0.8])


    def __init__(self, **kwargs):
        super(MapView, self).__init__(**kwargs)
        Logger.info("about to init the keyboard....")
        try:
            self._keyboard = Window.request_keyboard(self._keyboard_closed, self, 'text')
            self._keyboard.bind(on_key_down=self._on_keyboard_down)
        except:
            Logger.exception('keyboard couldnt be loaded!')

    def _keyboard_closed(self):
        print('My keyboard have been closed!')
        #self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        #self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        #print('The key', keycode, 'have been pressed'),(' - text is %r' % text),(' - modifiers are %r' % modifiers)
        if self.mapview_is_active==True:
            #print " textinput_is_active:", self.textinput_is_active, keycode, modifiers
            # Keycode is composed of an integer + a string
            # If we hit escape, release the keyboard
            if self.textinput_is_active == False:
                if len(modifiers)>0:
                    if modifiers[0]=="ctrl":
                        if keycode[1]=="s":
                            self.save_map_to_file()
                if keycode[1] == 'escape':
                    #pass
                    keyboard.release()
                    return True
                elif keycode[1]=="left":
                    self.select_father()
                elif keycode[1]=="right":
                    self.select_first_child()
                elif keycode[1]=="up":
                    self.select_sibling(1)
                elif keycode[1]=="down":
                    self.select_sibling(-1)
                elif keycode[1]=="insert":
                    #add a new childnode to the selected node:
                    self.get_selected_node().add_child()
                elif keycode[1]=="backspace" or keycode[1]=="delete":
                    #delete the selected node
                    #but first, check if there is no nodeInput open:
                    if self.textinput_is_active==False:
                        self.delete_selected_node()
                        #self.delete_node_by_ID(self.selectedNodeID)
                elif keycode[1]=="spacebar":
                    self.get_selected_node().fold_unfold()
                elif keycode[1]=="f2":
                    self.get_selected_node().edit()
                elif keycode[1]=="enter":
                    self.add_sibling()
                elif keycode[1] in ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','ö','ä','ü']:
                    self.get_selected_node().edit(text)
                else:
                    pass
            else:
                if keycode[1] == 'enter':
                    if 'shift' in modifiers:
                        print "shift is pressed..."
                    else:
                        try:
                            self.children[0].on_text_validate(remove_enter=True)
                        except:
                            print "oh... no node.textinput"
            # Return True to accept the key. Otherwise, it will be used by
            # the system.
        return False

    def do_for_undo(self):
        #print "do...", self.undopos, len(self.undostack), self.undostack
        if self.undopos < -1:
            for i in xrange(self.undopos,-1,1):
                self.undostack.pop()
            self.undopos = -1

        self.undostack.append(deepcopy(self.firstnode))
        if len(self.undostack)>11:
            self.undostack.popleft()
        #print "do...", self.undopos, len(self.undostack), self.undostack

    def undo(self):
        #print "undo...", self.undopos, len(self.undostack), self.undostack
        if -(self.undopos) < len(self.undostack):
            self.undopos -= 1
            self.firstnode = self.undostack[self.undopos]
            self.rebuild_map(do_for_undo=False)
        else:
            Logger.info("No more undo possible")
        #print "undo...", self.undopos, len(self.undostack), self.undostack

    def redo(self):
        print "redo...", self.undopos, len(self.undostack), self.undostack
        if self.undopos < -1:
            self.undopos += 1
            self.firstnode =self.undostack[self.undopos]
            self.rebuild_map(do_for_undo=False)
        #print "redo...", self.undopos, len(self.undostack), self.undostack


    def read_map_from_file(self,filename):
        try:
            self.loaded_map_filename = filename
            Logger.info("parse: ", filename)
            self.tree = etree.parse(filename)
            Logger.info("parsed...")
            self.rootnode = self.tree.getroot()
            self.firstnode = self.rootnode.find("node")
            self.firstnode.set("FOLDED","False")
            Logger.info( "build_map...")
            self.build_map(self.firstnode)
        except Exception, e:
            Logger.error("couldnt read map from file: " + str(e))

    def rebuild_map(self,do_for_undo=True):
        if do_for_undo:
            self.do_for_undo()
        self.clear_widgets()
        #self.textinput_is_active = False
        firstnodepos = [0,0]
        newnode=Node()
        #color = self.config.get('settings','')
        self.height = newnode.create_itself(self.firstnode,self,firstnodepos,fathers_end_pos=[0,self.height/2])
        self.add_widget(newnode)
        self.get_selected_node_by_ID().selected = True

    def build_map(self,node):
        try:
            self.clear_widgets()
            if node.tag!="node":
                self.rootnode = node
                self.firstnode = node.find("node")
                self.firstnode.set("FOLDED","False")

            newnode=Node(fathers_end_pos=[20,0])
            firstnodepos = [0,0]
            self.height = newnode.create_itself(self.firstnode,self,firstnodepos)
            self.selectedNode = newnode
            self.add_widget(newnode)
        except Exception, e:
            Logger.error("couldn't build map...   " + str(e))
        return ""

    def deselect_all(self):
        for node in self.children:
            node.selected = False

    def get_selected_node(self):
        return self.selectedNode

#        if self.selectedNodeID == "0":
        for node in self.children:
            try:
                if node.selected==True:
                    return node
            except:
                Logger.error("get_selected_node: no node found!")
#        else:
#            for node in self.children:
#                if node.selected==self.selectedNodeID:
#                    return node
        return self.children[0]

    def add_sibling(self):
        self.get_selected_node().add_sibling()

    def get_selected_node_by_ID(self):

        if self.selectedNodeID == "0":
            return self.children[0]
        else:
            for node in self.children:
                if node.nid==self.selectedNodeID:
                    return node
        #print "upsala, ",node, " --------",self.selectedNodeID
        return self.children[0]

    def get_parent_node_by_ID(self,nodeID):
        if nodeID != "0" and nodeID != None:
            for parent in self.tree.getiterator():
                for child in parent:
                    #... work on parent/child tuple
                    if child.get("ID")==nodeID:
                        try:
                            return parent
                        except:
                            pass
        return "0"

    def get_first_child_node_by_parent_ID(self,nodeID):
        if nodeID != "0" and nodeID != None:
            for parent in self.tree.getiterator():
                for child in parent:
                    #... work on parent/child tuple
                    if parent.get("ID")==nodeID:
                        #print "dadadada--uhuhuhu- ", child
                        try:
                            if child.tag=="node":
                                return child
                        except:
                            Logger.info("nope: "+ child)
                            pass
        return "0"

    def select_first_child(self):
        thisnode=self.get_selected_node()
        try:
            thisnode.child_nodes[-1].selected=True
            thisnode.selected=False
        except:
            try:
                if thisnode.folded==True:
                    thisnode.unfold()
                    self.rebuild_map(do_for_undo=False)
                    thisnode=self.get_selected_node()
                    thisnode.child_nodes[-1].selected=True
                    thisnode.selected=False
            except:
                Logger.info( "no childs to select!")

    def select_sibling(self,direction=1):
        thisnode=self.get_selected_node()
        print "select_sister", thisnode.ntext,thisnode.text
        #print thisnode.siblings
        try:
            #print direction, thisnode.i_sibling,[x.text for x in thisnode.siblings], len(thisnode.siblings)
            thisnode.siblings[thisnode.i_sibling+direction-1].selected=True
            thisnode.selected=False
        except:
            try:
                thisnode.siblings[direction-1].selected=True
                thisnode.selected=False
            except:
                Logger.info( "no siblings to select!")

    def select_father(self):
        #deselect actual node:
        self.get_selected_node().selected = False
        #get the parent node, with the help of its ID
        parent_xml_node = self.get_parent_node_by_ID(self.selectedNodeID)
        parent_ID = parent_xml_node.get("ID")
        for node in self.children:
            if node.nid==parent_ID:
                node.selected = True


    def delete_selected_node(self):
        try:
            print "delete this node: ",
            thisnode = self.get_selected_node()
            thisnode.father_node.xmlnode.remove(thisnode.xmlnode)
            thisnode.father_node.selected = True
            self.selectedNodeID = thisnode.father_node.nid
        except Exception, e:
            Logger.error("Node-deletion failed.   " + str(e))
        self.rebuild_map(do_for_undo=True)

    def delete_node_by_ID(self,ID):
        # delete a node from the xml-tree, by selecting its ID-string ("ID_249823749")
        #"//node[@ID='" + ID + "']" # xpath to find a node with a specific ID
        self.get_parent_node_by_ID(ID).remove(self.tree.find("//node[@ID='" + ID + "']"))
        #self.get_selected_node_by_ID(ID).father_node.remove(self.xmlnode)
        #self.tree.remove(self.tree.find("//node[@ID='" + ID + "']"))
        self.rebuild_map(do_for_undo=True)

    def delete_node_by_node(self,node):
        ID=node.xmlnode.get("ID")
        self.delete_node_by_ID(ID)

    def save_map_to_file(self,filename=None):
        #test:
        #self.test_merge_two_mindmaps()
        Logger.info("about to save the map to file: ")
        #self.test_mergeNodes()
        if filename == None:
            filename=self.loaded_map_filename
        try:
            self.tree.write(filename)
            Logger.info("map saved to: "+ filename)
        except Exception, e:
            Logger.error("couldnt save map to " + filename + "   " + str(e))

    def save_map(self,node,filename):
        if filename == None:
            filename=self.loaded_map_filename
        if node==None:
            node = self.tree.getroot()
        try:
            etree.ElementTree(node).write(filename)
            Logger.info("node ... saved to: "+ filename)
        except Exception, e:
            Logger.error("couldnt save map to " + filename + "   " + str(e))

    def close_map(self):
        self.clear_widgets()
        self.rootnode=None
        self.firstnode=None

    def set_mapview_is_active(self, state):
        if state=='down': # down--> button-down--> active
            self.mapview_is_active = True
        else: # if state=='normal' --> not active
            self.mapview_is_active = False
        #self.app.activeMapView = self

    def generate_hashmap(self):
        try:
            from re import findall
        except Exception, e:
            Logger.error("couldnt import re (regularExpressions)...or copy...  " + str(e))
            return None
        try:
            #create a new xml-map
            Logger.info("...generate Hashmap..")
            hashroot = etree.Element('map')
            hashfirstnode = etree.SubElement(hashroot,'node')
            hashfirstnode.set("TEXT", "#Hashmap")
            #search the self.rootnode or self.firstnode for hashtags
            for xmlnode in self.rootnode.iter("node"):#.getiterator("node"):#xpath('//node'):
                #print xmlnode.get('TEXT')
                if '#' in xmlnode.get('TEXT'):
                    nodetext=xmlnode.get('TEXT')
                    #begin = nodetext.find('#')
                    #end_space =  nodetext.find(' ',begin)
                    #if end_space==-1:
                    #    end_space=None

                    #print "found it! " + nodetext + " ----------- " +nodetext[begin:end_space]
                    #regexp = re.compile(r'#[A-Za-z0-9_]+')
                    #for hashtag in findall("#[A-Za-z0-9_]+", nodetext):

                    for hashtag in findall("(#[A-Za-z0-9_]*)(:[A-Za-z0-9_]*)?", nodetext):
                        #find the matching hashnode for every hashtag in this node...
                        firstmatching_node = hashroot.find("./node/node[@TEXT='" + hashtag[0] + "']")
                        #print "match?: ", matching_node
                        if firstmatching_node!=None:
                            #print "-*- okay:  ", matching_node.get("TEXT")
                            pass
                        #if there is no matching hashnode jet, create one:
                        else:
                            firstmatching_node = etree.SubElement(hashfirstnode,'node')
                            firstmatching_node.set("TEXT", hashtag[0])
                            firstmatching_node.set("ID", "ID_"+ str(randint(1000000000,10000000000)))

                        if hashtag[1]!='':
                            #a subhashtag!
                            secondmatching_node = firstmatching_node.find("./node[@TEXT='" + hashtag[0] + hashtag[1] + "']")

                            if secondmatching_node ==None:
                                secondmatching_node = etree.SubElement(firstmatching_node,'node')
                                secondmatching_node.set("TEXT", hashtag[0] + hashtag[1])
                                secondmatching_node.set("ID", "ID_"+ str(randint(1000000000,10000000000)))

                            secondmatching_node.append(deepcopy(xmlnode))
                        else:

                           # for hashtagdouble in findall("#([A-Za-z0-9_])*:([A-Za-z0-9_])*", nodetext):
                           #     print "h:h:   ", hashtagdouble
                           #
                           #     if double_point_is_there ==True:
                           #         matching_node = hashroot.find("./node/node[@TEXT='" + hashtag + "']/node[@TEXT='" + hashlayer2 + "']")


                            #add the xmlnode to the hashnode
                            firstmatching_node.append(deepcopy(xmlnode))

                                 #hashfirstnode = etree.SubElement(hashroot,'node')
            print hashfirstnode#, hashfirstnode.tostring()
            #etree.dump(hashroot)
            return hashroot
        #now we have a xml-hashmap. next step: display it in a new tab

        except Exception, e:
            Logger.error("couldn't create the hashmap!  " + str(e))
            return None


    def test_merge_two_mindmaps(self):
        filenameA = 'mergeA.mm'
        filenameB = 'mergeB.mm'
        filenameold = 'mergeold.mm'

        xmla = etree.parse(filenameA)
        xmlb = etree.parse(filenameB)
        xmlold = etree.parse(filenameold)

        self.merge_two_mindmaps(xmla,xmlb,xmlold)

        print "parsed..."
        #self.rootnode = self.tree.getroot()
        #self.firstnode = self.rootnode.find("node")

    def merge_two_mindmaps(self,xmlmapa,xmlmapb,xmlmaproot=None):
        xmlmapnew=xmlmapb

        for nodea in xmlmapa.iter('node'):
            #print nodea, nodea.get('text'), nodea.get('TEXT')
            nodeb = xmlmapb.find(".//node[@ID='" + nodea.get('ID') + "']")
            #print "nodeA-ID:", nodea.get("ID")," , nodeb.id: ",nodeb.get("ID")
            if nodeb!= None:
                print "the node is in both maps"
                if nodeb.get('MODIFIED')==nodea.get('MODIFIED'):
                    print "same same"
                else:
                    print "oh! modified!",nodea.get('MODIFIED'),nodeb.get('MODIFIED')
                    if int(nodea.get('MODIFIED'))>int(nodeb.get('MODIFIED')):
                        print "a was later!"
            else:
                print "nodea existiert in map-b leider nicht"
                #add nodea to xmlmapnew
                # we need the location!
                # with lxml this would be: ..node..getpath() #-->map/node/node/node[3]


    def test_mergeNodes(self):

        print "44444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444"
        filenameA = 'mergeA.mm'
        filenameB = 'mergeB.mm'
        filenameold = 'mergeold.mm'

        xmla = etree.parse(filenameA)
        xmlb = etree.parse(filenameB)
        xmlold = etree.parse(filenameold)

        Logger.info("parsed...")

        nodea = xmla.find("node")
        nodeb = xmlb.find("node")
        nodeold = xmlold.find("node")

        nodenew = deepcopy(nodea)
        #nodenew = etree.Element("node")
        #print("...h1", etree.tostring(nodea))#, pretty_print=True))
        #print("...h2", etree.tostring(nodeb))


        self.mergeNodes(nodea,nodeb,nodenew)
        #print("...h3", etree.tostring(nodea))#, pretty_print=True))
        #print("...h4", nodea,nodenew)
        #print("...h5", etree.tostring(nodenew))

        mapNewElement = etree.Element("map")
        mapNewElement.append(nodenew)
        self.save_map(mapNewElement,"mergednew.mm")
        #self.rootnode = self.tree.getroot()
        #self.firstnode = self.rootnode.find("node")

    def mergeActualMapWithRemoteLocation(self):
        try:
            from os.path import basename, join, isfile
            self.save_map_to_file()
            self.save_map_to_file(self.loaded_map_filename+ ".pre_merge.mm")

            filenameA = self.config.get("files","filename")
            filenameB = join(self.config.get("files","remotedir") , basename(self.config.get("files","filename")))
            if isfile(filenameA) == False:
                Logger.error("No File Loaded!?!!" + filenameA)
                popup = Popup(title='No Map loaded!?', content=Label(text=filenameA + '  is invalid. try to load or create a Map'), size_hint=(0.6,0.3))
                popup.open()
                return 0
            elif  isfile(filenameB) == False:
                Logger.error("")
                popup = Popup(title='No remote Map!', content=Label(text=filenameB + '  is invalid. Adjust the path for remote location under Settings->Files!', text_size=(self.width/3,None)), size_hint=(0.6,0.3))
                popup.open()
                return 0


            Logger.info("merging.......       " + filenameA + "   ;   " + filenameB)

            xmla = etree.parse(filenameA)
            xmlb = etree.parse(filenameB)

            nodea = xmla.find("node")
            nodeb = xmlb.find("node")
            nodenew = deepcopy(nodea)

            self.mergeNodes(nodea,nodeb,nodenew)


            mapNewElement = etree.Element("map")
            mapNewElement.append(nodenew)
            self.save_map(mapNewElement, filenameA)
            self.save_map(mapNewElement, filenameA + ".old.mm")
            self.save_map(mapNewElement, filenameB)
            self.save_map(mapNewElement, filenameB + ".old.mm")
            self.read_map_from_file(filenameA)
        except Exception, e:
            Logger.error("couldn't finish the merging-process!  " + str(e))

    def mergeNodes(self,nodea,nodeb,nodenew,nodeold=None):
        #print "...........................................", nodea.get('TEXT')#, nodeb.get('TEXT')
        bool_found_the_same_node_id = False
        i_a=-1
        i_b=-1

        #remove all childnodes from nodenew to insert them later again (no need to remove them later....
        for nodenewchild in nodenew.findall("node"):
            nodenew.remove(nodenewchild)

        for nodebchild in nodeb.findall("node"):
            i_b+=1
            #print "...........................", nodebchild.get('TEXT')
            bool_found_the_same_node_id = False
            for nodeachild in nodea.findall("node"):
                i_a+=1
                if nodeachild.get("ID")==nodebchild.get("ID"):
                    bool_found_the_same_node_id = True
                    #print "found the same child in a and b.  ",
                    if nodeachild.get('MODIFIED')==nodebchild.get('MODIFIED'):
                        #print " ..they have the same modify-dates... :",nodeachild.get('MODIFIED'),nodebchild.get('MODIFIED')
                        newchildnode = deepcopy(nodebchild)
                        nodenew.insert(i_b,newchildnode) #not necessary, just keep it
                    else:
                        Logger.info( "merge ..they have different modify-dates.. :" + nodeachild.get('MODIFIED')+nodebchild.get('MODIFIED')+ int(nodeachild.get('MODIFIED'))+ int(nodebchild.get('MODIFIED')))
                        if int(nodeachild.get('MODIFIED'))> int(nodebchild.get('MODIFIED')):
                            #print ";  nodea was later. "
                            newchildnode = deepcopy(nodeachild)
                            nodenew.insert(i_a,newchildnode)
                        else:
                            #print ";  nodeb was later. "
                            newchildnode = deepcopy(nodebchild)
                            nodenew.insert(i_b,newchildnode)

                    self.mergeNodes(nodeachild,nodebchild,newchildnode)

            if bool_found_the_same_node_id==False:
                #couldnt find a nodeachild with the same ID:
                Logger.info("     coulnt find nodeb in a      "+ nodebchild.get('TEXT'))
                nodenew.insert(i_b,nodebchild)

        #insert all childnodes that exist only in nodea:
        i_a=-1
        for nodeachild in nodea.findall("node"):
            i_a+=1
            bool_found_the_same_node_id = False
            for nodebchild in nodeb.findall("node"):
                if nodeachild.get("ID")==nodebchild.get("ID"):
                    bool_found_the_same_node_id = True

            if bool_found_the_same_node_id==False:
                #couldnt find a nodebchild with the same ID:
                Logger.info( "     coulnt find nodea in b      "+ nodeachild.get("TEXT"))
                nodenew.insert(i_a,nodeachild)


class MapDropDown(DropDown):
    app = None

    def delete_selected_node(self):
        self.app.activeMap.delete_selected_node()


class MindmapApp(FloatLayout):
    mv=ObjectProperty()
    mv2=ObjectProperty()
    activeMap=mv
    app=ObjectProperty()
    tabpanel=ObjectProperty()
    startmenu = ObjectProperty()

    def __init__(self, **kwargs):
        super(MindmapApp, self).__init__(**kwargs)
        self.mv.app = self.app
        #bt_open_last_map
        #self.startmenu.add_widget()


    def load_map(self,filename):
        try:
            self.mv.config=self.app.config
            self.mv2.config=self.app.config
            print "close map"
            self.mv.close_map()
            Logger.info("open map from file: " + filename)
            self.mv.read_map_from_file(filename)
            Logger.info("map loaded!" +  filename)
            self.app.config.set('files','filename',filename)
        except Exception, e:
            Logger.error("oh, loading " + filename + " didn't work...?")
        self.dismiss_popup()
        print self.tabpanel

    def create_new_map(self):
        self.save_map()
        Logger.info("create a new map " + self.tabpanel.current_tab.state)
        Popup(title="Enter new Filename, click outside to create the File",
              content=TextInput(focus=True, multiline=False),
              size_hint=(0.72, 0.30),
              on_dismiss=self.copy_new_map).open()

    def copy_new_map(self, popup):
        newname = popup.content.text
        Logger.info ("Create a new map. Filename: " + newname + newname)
        try:
            if newname[-3:]!=".mm":
                newname += ".mm"
            file = open(newname, 'a')
            file.write('<map version="1.0.1"><node CREATED="1404831683705" FOLDED="False" ID="ID_239640550" MODIFIED="1404831683705" TEXT="New Mindmap"/></map>')
            file.close()
            #copyfile("new.mm", newname)
            self.load_map(newname)
        except Exception, e:
            Logger.error("couldn't create a new file with the filename " + newname + str(e))



    def dismiss_popup(self):
        try:
            self._popup.dismiss()
        except:
            pass

    def show_load(self):
        content = LoadDialog(load=self.load_map, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content, size_hint=(0.9, 0.9))
        self._popup.open()

    def save_map(self):
        self.mv.save_map_to_file()


class LoadDialog(ModalView):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)

class mmviewApp(App):
    #config

    def build(self):
        self.config.set('kivy', 'exit_on_escape', '0')
        self.mindmapapp=MindmapApp(app=self)
        global MIN_NODE_WIDTH
        global MAX_NODE_WIDTH
        MIN_NODE_WIDTH = int(self.config.get("options","min_node_width"))
        MAX_NODE_WIDTH = int(self.config.get("options","max_node_width"))
        print "MIN_NODE_WIDTH", MIN_NODE_WIDTH
        self.mindmapapp.load_map(self.config.get("files","filename"))
        return self.mindmapapp

    def on_config_change(self, config, section, key, value):
        global MIN_NODE_WIDTH
        global MAX_NODE_WIDTH
        if config is self.config:
            token = (section, key)
            if token == ('options', 'min_node_width'):
                MIN_NODE_WIDTH = int(self.config.get("options","min_node_width"))
            elif token == ('options', 'max_node_width'):
                # print('Key1 has been changed to', value)
                MAX_NODE_WIDTH = int(self.config.get("options","max_node_width"))
            elif token == ('section1', 'key2'):
                pass

    def build_config(self, config):
        config.setdefaults('files', {'filename': 'new.mm','key1': 'blabla','key2': '42','remotedir':'./remote'})
        config.setdefaults('options', {'min_node_width': '30','max_node_width': '600'})
        config.setdefaults('kivy', {'exit_on_escape': '0'})

    def build_settings(self, settings):
        jsondata = """
[
    { "type": "title",
      "title": "Mindbike  File Preferences" },

    { "type": "string",
      "title": "Filename",
      "desc": "The default loaded map",
      "section": "files",
      "key": "filename" },

    { "type": "string",
      "title": "Remotedir",
      "desc": "Remote folder for map-merging",
      "section": "files",
      "key": "remotedir" },

    { "type": "options",
      "title": "My first key",
      "desc": "Description of my first key",
      "section": "files",
      "key": "key1",
      "options": ["value1", "value2", "another value"] },

    { "type": "numeric",
      "title": "Minimum Node width",
      "desc": "Minimum Node width",
      "section": "options",
      "key": "min_node_width" },

    { "type": "numeric",
      "title": "Maximum Node width",
      "desc": "Maximum Node width",
      "section": "options",
      "key": "max_node_width" }
]
"""
        settings.add_json_panel('Mindbike Preferences',
            self.config, data=jsondata)

    def on_pause(self):
      # loosing context on Android, iOS
      Logger.info("pause...")
      self.mindmapapp.save_map()
      self.config.write()
      return True

    def on_stop(self):
        self.on_pause()

if __name__ == '__main__':
    mmviewApp().run()
