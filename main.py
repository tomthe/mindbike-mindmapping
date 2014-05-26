# -*- coding: utf-8 -*-

import kivy
from kivy.uix.modalview import ModalView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ListProperty, StringProperty,ObjectProperty, BooleanProperty
from kivy.app import App
from random import randint
import time
#from readmm import stringize
from lxml import etree


kivy.require('1.0.7')

class NodeTextInput(TextInput):
    node=None

    def __init__(self,**kwargs):
        #print "node kwargs:", kwargs
        self.node=kwargs['node']
        #self.bind(focus=self.on_focus)
        super(NodeTextInput, self).__init__(**kwargs)

    def on_text_validate(self):
        newtext=self.text
        self.node.text=unicode(newtext,'utf-8')
        self.node.on_text2()
        self.node.remove_widget(self)

    def on_focus(self,instance,value):
        if value:
            pass
            #print "focus",instance, ",-, ", value
        else:
            #print "defocus",instance, ",-, ", value
            self.on_text_validate()

        return super(NodeTextInput, self).on_focus(instance,value)

    def on_enter(self,instance,value):
        pass
        # print "enter gedrueckt!!"


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

    def on_selected(self,instance,value):
        #self.rootwidget.deselect_all()
        if value:
            self.bgcolor = [0.3,0.1,0.1]
        else:
            self.bgcolor = [0.25,0.25,0.25]

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
            else:
                #self.fold_unfold()
                self.selected = not self.selected
        return super(Node, self).on_touch_down(touch)

    def edit(self):
        inputsize = self.size[0]+66, self.size[1]+24
        textinput = NodeTextInput(node=self,size=inputsize, pos=self.pos,text=self.text, focus=True, multiline=False)
        self.add_widget(textinput,-1)


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
        self.xmlnode.set(u"TEXT",unicode(self.text,))
        self.rootwidget.rebuild_map()

    def add_child(self):
        #einen neuen "node" erstellen
        #<node TEXT="knot1-2" ID="ID_1021949625" CREATED="1400192771540" MODIFIED="1400197616894">
        #TEXT="nimi" ID="ID_1004240095" CREATED="140 062 763 512 6" MODIFIED="1400627638635"

        newxmlnode = etree.Element("node")
        #The Text is empty
        TEXT="_"
        #a random ID between 10E9 and 10E10:
        ID = "ID_"+ str(randint(1000000000,10000000000))
        #Seconds since epoch:
        CREATED = str(round(time.time()))

        #set the xml-node-Attributes:
        newxmlnode.set("TEXT",TEXT)
        newxmlnode.set("ID",ID)
        newxmlnode.set("CREATED",CREATED)
        newxmlnode.set("MODIFIED",CREATED)
        self.xmlnode.set("FOLDED","False")
        self.xmlnode.insert(0,newxmlnode)
        self.rootwidget.rebuild_map()

    def create_itself(self,xmlnode,rootwidget,pos,unfold=False,fathers_end_pos=[20,20],fathers_width=50):
        if xmlnode.tag=="node":
            #print "fathersendpos.pos, self.ext: (nnerhalb...,", self.fathers_end_pos,self.text, "fathers..."
            self.xmlnode = xmlnode
            self.rootwidget = rootwidget
            self.fathers_end_pos= fathers_end_pos
            self.fathers_width = fathers_width
            self.text = xmlnode.get("TEXT")
            self.texture_update()
            self.size = self.texture_size
            self.bby = self.height+4
            self.pos = pos
            childpos=[pos[0]+self.size[0]+70,pos[1]]
            has_open_children = False
            if xmlnode.get("FOLDED",default="False")=="False" or unfold==True:
                xmlnode.set("FOLDED","False")
                self.folded=False
                for nodechild in xmlnode:
                    if nodechild.tag=="node":
                        has_open_children=True

                        newnode = Node()
                        #print "self.pos, self.ext: (nnerhalb...,",self.pos,self.text
                        # newnode.canvas.
                        childboxy = newnode.create_itself(nodechild,rootwidget,childpos,fathers_end_pos= self.pos,fathers_width=self.width)
                        rootwidget.add_widget(newnode)
                        #self.childnodes.append(newnode)
                        childpos[1]  += childboxy
                        self.bby += childboxy

                if has_open_children:
                    pass
                    #print "has open children, ", self.text
                    self.bby -= self.height
                    #self.xmlnnode
                    self.pos[1] += self.bby/2 - self.height/2 -4

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


class MapView(FloatLayout):
    rootnode=None
    firstnode=None

    def read_map_from_file(self,filename):
        tree = etree.parse(filename)
        self.rootnode = tree.getroot()
        self.firstnode = self.rootnode.find("node")
        self.firstnode.set("FOLDED","False")
        self.build_map(self.firstnode,0,"")

    def rebuild_map(self):
        self.clear_widgets()
        firstnodepos = [0,0]
        newnode=Node()
        self.height = newnode.create_itself(self.firstnode,self,firstnodepos,fathers_end_pos=[0,self.height/2])
        self.add_widget(newnode)

    def build_map(self,node,level,outstr):
        if node.tag=="node":
            newnode=Node(fathers_end_pos=[20,0])
            firstnodepos = [0,0]
            self.height = newnode.create_itself(node,self,firstnodepos)
            self.add_widget(newnode)
        else:
            print "what?", node.tag
        return outstr

    def deselect_all(self):
        for node in self.children:
            node.selected = False


class MindmapApp(FloatLayout):
    mv=ObjectProperty()

    def load_map(self,filename):
        self.mv.read_map_from_file(filename)

class mmviewApp(App):

    def build(self):
        mindmapapp=MindmapApp()
        mindmapapp.load_map("testtemp.mm")
        return mindmapapp

if __name__ == '__main__':
    mmviewApp().run()