# -*- coding: utf-8 -*-

# MindBike Mindmapping - Mindmap viewer and editor for mobile devices and desktop platforms
# Copyright (C) 2014 Tom Theile
# This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 3 of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this program; if not, see <http://www.gnu.org/licenses/>.

import kivy
from kivy.app import App
from kivy.config import Config
from kivy.uix.modalview import ModalView
from kivy.uix.boxlayout import BoxLayout
#from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ListProperty, StringProperty,ObjectProperty, BooleanProperty
from kivy.uix.popup import Popup
from kivy.logger import Logger
from kivy.core.window import Window
from random import randint
import time
from ast import literal_eval

#from readmm import stringize
try:
  from lxml import etree
  print("running with lxml.etree")
except ImportError:
  try:
    # Python 2.5
    import xml.etree.cElementTree as etree
    print("running with cElementTree on Python 2.5+")
  except ImportError:
    try:
      # Python 2.5
      import xml.etree.ElementTree as etree
      print("running with ElementTree on Python 2.5+")
    except ImportError:
      try:
        # normal cElementTree install
        import cElementTree as etree
        print("running with cElementTree")
      except ImportError:
        try:
          # normal ElementTree install
          import elementtree.ElementTree as etree
          print("running with ElementTree")
        except ImportError:
          print("Failed to import ElementTree from any known place")


kivy.require('1.0.7')

class NodeTextInput(TextInput):
    node=None

    def __init__(self,**kwargs):
        print "node kwargs:", kwargs
        self.size_hint = (None,None)
        self.node=kwargs['node']
        self.node.rootwidget.textinput_is_active = True
        #self.bind(focus=self.on_focus)
        super(NodeTextInput, self).__init__(**kwargs)

    def on_text_validate(self,remove_enter=False):
        if remove_enter:
            self.text = self.text[:-1]
        print "on_text_validate1-1", self.node.text, "|||",self.text
        newtext=self.text
        self.node.text=unicode(newtext,'utf-8')
        self.node.rootwidget.textinput_is_active = False
        #self.node.rootwidget.textinput  = None
        if self.parent:
            print "888888888888888888888888888888888888 parent vorhanden! parent!"
            self.parent.remove_widget(self)
        else:
            print "77777777777777777777777777777777777arg kein parent!"
        self.focus=False
        self.node.on_text2()
        self.node.rootwidget.rebuild_map()

    def on_focus(self,instance,value):
        if value:
            pass
        else:
            self.on_text_validate()
            pass
        return super(NodeTextInput, self).on_focus(instance,value)

    def on_enter(self,instance,value):
        print "enter gedrueckt!!"
        pass

    def on_text(self,instance,value):
        #print "line numbers: ", value.count('\n')
        #self.height = (1 + value.count('\n')) * 22
        self.adjust_input_size()

    def adjust_input_size(self):
        self.height = (1 + self.text.count('\n')) * 19 + 10
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
    bgcolor = ListProperty([.25,0.25,0.25])
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
            self.bgcolor = [0.3,0.1,0.1]
            self.rootwidget.selectedNodeID=self.xmlnode.get("ID")
            self.rootwidget.selectedNode=self
            #print self.pos, self.parent.size,self.parent.parent.size, self.parent.parent.scroll_x,self.parent.parent.scroll_y
            self.get_optimal_scroll_pos()
        else:
            self.bgcolor = [0.25,0.25,0.25]

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
        except:
            pass

    def set_posright(self,value):
        self.pos= [value[0] - self.width, value[1]]

    def get_posright(self):
        return [self.x + self.width,self.y]

    def on_touch_down(self, touch):
        self.selected =False
        if self.collide_point(*touch.pos):
            if touch.is_double_tap:
                print "double!!! ", self.text, self.pos,self.size
                self.edit()
            #elif touch.
            else:
                #self.fold_unfold()
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
            print "single-fold! ", self.text, self.pos,self.size
            self.fold()
        else:
            print "single-de-fold!! unfold! ", self.text, self.pos,self.size
            self.unfold()
        self.rootwidget.rebuild_map()

    def fold(self):
        #print "fold:  ", self.text
        self.folded = True
        self.xmlnode.set("FOLDED","True")

    def unfold(self):
        #print "unfold, "
        self.folded = False
        self.xmlnode.set("FOLDED","False")
        self.create_itself(self.xmlnode,self.rootwidget,[self.x,self.y],unfold=True)

    def on_text2(self):
        #print "on_text",unicode(self.text)#,instance,value
        #self.width=self.texture_size[0]
        if self.text[0]=="=":
            #try:
                self.text=str(literal_eval(self.text[1:]))
            #except:
                pass
                print "eval: ", str(self.text)
                print "evaluieren:  ",str(eval("23*5")),str(literal_eval("23*5"))
        self.xmlnode.set(u"TEXT",unicode(self.text,))
        #self.rootwidget.rebuild_map()

    def add_sibling(self):
        n_siblings = len(self.siblings)
        print self.siblings
        print ([x.tag for x in self.father_node.xmlnode])
        n_non_node_xmls = len([x.tag for x in self.father_node.xmlnode]) - n_siblings
        n_non_node_xmls_until_now = len([x.tag for x in self.father_node.xmlnode][self.i_sibling-1:]) - [x.tag for x in self.father_node.xmlnode][self.i_sibling-1:].count("node")
        print "n_siblings:", n_siblings, " not-node-xmls: ", n_non_node_xmls, "; i_sibling: ", self.i_sibling, "; n_non_node_xmls_until_now: ", n_non_node_xmls_until_now
        position = len(self.siblings) - self.i_sibling + 1 + n_non_node_xmls_until_now
        print "p, p2: ", position
        self.father_node.add_child(position)

    def add_child(self,position=200):
        #einen neuen "node" erstellen
        #<node TEXT="knot1-2" ID="ID_1021949625" CREATED="1400192771540" MODIFIED="1400197616894">
        #TEXT="nimi" ID="ID_1004240095" CREATED="140 062 763 512 6" MODIFIED="1400627638635"
        print position, "add...                                       ----"
        newxmlnode = etree.Element("node")
        #The Text is empty
        TEXT="_"
        #a random ID between 10E9 and 10E10:
        ID = "ID_"+ str(randint(1000000000,10000000000))
        self.nid=ID
        #Seconds since epoch:
        CREATED = str(int(time.time()*1000))

        #set the xml-node-Attributes:
        newxmlnode.set("TEXT",TEXT)
        newxmlnode.set("ID",ID)
        newxmlnode.set("CREATED",CREATED)
        newxmlnode.set("MODIFIED",CREATED)
        newxmlnode.set("SELECTED","TRUE")
        self.xmlnode.set("FOLDED","False")

        print position, "position"
        self.xmlnode.insert(position,newxmlnode)
        self.rootwidget.rebuild_map()

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
            self.bby = self.height + self.VERTICAL_MARGIN
            self.pos = pos
            self.i_sibling =i_sibling
            #print i_sibling, self.text
            i_sibling_for_children=0
            childpos=[pos[0]+self.size[0]+70,pos[1]]
            has_open_children = False
            if self.xmlnode.get("SELECTED","False")=="TRUE":
                print "selected!!!"
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
                        #print "self.pos, self.ext: (nnerhalb...,",self.pos,self.text
                        # newnode.canvas.
                        childboxy = newnode.create_itself(nodechild,rootwidget,childpos,fathers_end_pos= self.pos,fathers_width=self.width, father_node=self,i_sibling=i_sibling_for_children)

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
                            print "--------------------------------------ohohohoho",self.text
                    else:
                        print "-----------------------------------------height"
                        self.bby = self.height
            else:
                self.folded = True
                #print "folded: ",self.text,xmlnode.find("node")
                #print(etree.tostring(self.xmlnode, pretty_print=True))
                if xmlnode.find("node") !=None:
                    #print " has folded kids", self.text
                    self.bgcolor = [.4,0.4,0.4]
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
        #print('The key', keycode, 'have been pressed')
        #print(' - text is %r' % text)
        #print(' - modifiers are %r' % modifiers)
        print " textinput_is_active:", self.textinput_is_active, keycode, modifiers
        # Keycode is composed of an integer + a string
        # If we hit escape, release the keyboard
        if self.textinput_is_active == False:
            if len(modifiers)>0:
                if modifiers[0]=="ctrl":
                    if keycode[1]=="s":
                        self.save_map_to_file()
            if keycode[1] == 'escape':
                keyboard.release()
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
                pass
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
                        print "enter4",self.children[0].text, self.children
                        self.children[0].on_text_validate(remove_enter=True)
                    except:
                        print "oh... no node.textinput"
        # Return True to accept the key. Otherwise, it will be used by
        # the system.
        return False

    def read_map_from_file(self,filename):
        try:
            self.loaded_map_filename = filename
            print "parse:", filename
            self.tree = etree.parse(filename)
            print "parsed..."
            self.rootnode = self.tree.getroot()
            self.firstnode = self.rootnode.find("node")
            self.firstnode.set("FOLDED","False")
            print "build_map..."
            self.build_map(self.firstnode,0,"")
        except:
            print "file doesn't exist!"

    def rebuild_map(self):
        self.clear_widgets()
        #self.textinput_is_active = False
        firstnodepos = [0,0]
        newnode=Node()
        self.height = newnode.create_itself(self.firstnode,self,firstnodepos,fathers_end_pos=[0,self.height/2])
        self.add_widget(newnode)
        self.get_selected_node_by_ID().selected = True

    def build_map(self,node,level,outstr):
        if node.tag=="node":
            newnode=Node(fathers_end_pos=[20,0])
            firstnodepos = [0,0]
            self.height = newnode.create_itself(node,self,firstnodepos)
            self.selectedNode = newnode
            self.add_widget(newnode)
        else:
            print "what?", node.tag
        return outstr

    def deselect_all(self):
        for node in self.children:
            node.selected = False

    def get_selected_node(self):
        return self.selectedNode

#        if self.selectedNodeID == "0":
        for node in self.children:
            try:
                if node.selected==True:
                    print "get_selected_node: node found"
                    return node
            except:
                print "get_selected_node: not-node-error"
                pass
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
        print "upsala, ",node, " --------",self.selectedNodeID
        return self.children[0]

    def get_parent_node_by_ID(self,nodeID):
        if nodeID != "0" and nodeID != None:
            for parent in self.tree.getiterator():
                for child in parent:
                    #... work on parent/child tuple
                    if child.get("ID")==nodeID:
                        try:
                            print parent, "  -  "#, parent.ntext
                            return parent
                        except:
                            pass
        return "0"

    def get_first_child_node_by_parent_ID(self,nodeID):
        if nodeID != "0" and nodeID != None:
            for parent in self.tree.getiterator():
                for child in parent:
                    print "dadadada--- ", child
                    #... work on parent/child tuple
                    if parent.get("ID")==nodeID:
                        print "dadadada--uhuhuhu- ", child
                        try:
                            print child.tag
                            print child, child.tag=='node'
                            if child.tag=="node":
                                return child
                        except:
                            print "nope: ", child
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
                    self.rebuild_map()
                    thisnode=self.get_selected_node()
                    thisnode.child_nodes[-1].selected=True
                    thisnode.selected=False
            except:
                print "no childs to select!"

    def select_sibling(self,direction=1):
        thisnode=self.get_selected_node()
        print "select_sister", thisnode.ntext,thisnode.text
        #print thisnode.siblings
        try:
            print direction, thisnode.i_sibling,[x.text for x in thisnode.siblings], len(thisnode.siblings)
            thisnode.siblings[thisnode.i_sibling+direction-1].selected=True
            thisnode.selected=False
        except:
            try:
                print "ohoh,"
                thisnode.siblings[direction-1].selected=True
                thisnode.selected=False
            except:
                print "no siblings to select!"

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
            print "delet this node:",
            thisnode = self.get_selected_node()
            thisnode.father_node.xmlnode.remove(thisnode.xmlnode)
            thisnode.father_node.selected = True
        except:
            print "exception: deletion failed"
        self.rebuild_map()

    def delete_node_by_ID(self,ID):
        # delete a node from the xml-tree, by selecting its ID-string ("ID_249823749")
        #"//node[@ID='" + ID + "']" # xpath to find a node with a specific ID
        self.get_parent_node_by_ID(ID).remove(self.tree.find("//node[@ID='" + ID + "']"))
        #self.get_selected_node_by_ID(ID).father_node.remove(self.xmlnode)
        #self.tree.remove(self.tree.find("//node[@ID='" + ID + "']"))
        self.rebuild_map()

    def delete_node_by_node(self,node):
        ID=node.xmlnode.get("ID")
        self.delete_node_by_ID(ID)

    def save_map_to_file(self,filename=None):
        if filename == None:
            filename=self.loaded_map_filename
        try:
            self.tree.write(filename)
            print "map saved to: ", filename
        except:
            Logger.error("couldnt save map to " + filename)

    def close_map(self):
        self.clear_widgets()
        self.rootnode=None
        self.firstnode=None

class MindmapApp(FloatLayout):
    mv=ObjectProperty()
    app=ObjectProperty()

    def load_map(self,filename):
        try:
            print "close map"
            self.mv.close_map()
            print "open map from file: ", filename
            self.mv.read_map_from_file(filename)
            print "map loaded!", filename
            self.app.config.set('files','filename',filename)
        except:
            print "oh, loading ",filename, " didn't work... try again?"
            try:
                self.show_load()
            except:
                Logger.error("couldnt show the load-dialog")
        self.dismiss_popup()


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
        self.mindmapapp.load_map(self.config.get("files","filename"))
        return self.mindmapapp

    def build_config(self, config):
        config.setdefaults('files', {
            'filename': 'new.mm',
            'key1': 'blabla',
            'key2': '42'
        })

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

    { "type": "options",
      "title": "My first key",
      "desc": "Description of my first key",
      "section": "files",
      "key": "key1",
      "options": ["value1", "value2", "another value"] },

    { "type": "numeric",
      "title": "My second key",
      "desc": "Description of my second key",
      "section": "files",
      "key": "key2" }
]
"""
        settings.add_json_panel('Mindbike Preferences',
            self.config, data=jsondata)

    def on_pause(self):
      # loosing context on Android, iOS
      print "pause..."
      self.mindmapapp.save_map()
      self.config.write()
      return True

    def on_stop(self):
        self.on_pause()

if __name__ == '__main__':
    mmviewApp().run()
