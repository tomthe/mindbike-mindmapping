
import kivy
from kivy.uix.modalview import ModalView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ListProperty, StringProperty,ObjectProperty
from kivy.app import App
#from readmm import stringize
from lxml import etree


kivy.require('1.0.7')

class Node(Label):
    ntext = StringProperty()
    folded = False
    bbox=[100,15]
    nid=""
    childnodes = ListProperty([])
    nodetextlabel = ObjectProperty()
    xmlnode = None
    
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if touch.is_double_tap:
                print "double!!! ", self.text, self.pos,self.size
            else:
                
                if self.folded==False:
                    print "single-fold! ", self.text, self.pos,self.size
                    self.fold()
                else:
                    print "single-de-fold!! unfold! ", self.text, self.pos,self.size
                    self.unfold()
            
    def fold(self):
        print "fold:  ", self.text
        self.folded = True
        for child in self.childnodes:
            child.fold()
            self.rootwidget.remove_widget(child)
        #for child in self.childnodes:
    
    def unfold(self):
        print "unfold, "
        self.folded = False
        self.create_itself(self.xmlnode,self.rootwidget,[self.x,self.y],unfold=True)
        
    def create_itself(self,xmlnode,rootwidget,pos,unfold=False):
        if xmlnode.tag=="node":
            self.xmlnode = xmlnode
            self.rootwidget = rootwidget
            self.text = xmlnode.get("TEXT")
            self.texture_update()
            self.size = self.texture_size
            self.bbox = [self.size[0],self.size[1]]
            self.pos=[pos[0],pos[1]]
                    
            childpos=[pos[0]+self.size[0]+30,pos[1]]
            if xmlnode.get("FOLDED",default="False")=="False" or unfold==True:
                xmlnode.set("FOLDED","False")
                self.folded=False
                for nodechild in xmlnode:
                    if nodechild.tag=="node":
                        print "childnode... ", childpos, self.pos, "--",self.size
                        newnode = Node()
                        #childpos=(childpos[0],childpos[1])
                        childboxy = newnode.create_itself(nodechild,rootwidget,childpos)
                        rootwidget.add_widget(newnode)
                        #self.add_widget(newnode)
                        self.childnodes.append(newnode)
                        childpos[1]  += childboxy
                        self.bbox[1] += childboxy
            else:
                self.folded = True
            #self.size = [self.nwidth,self.nheight]
            
            return self.bbox[1]
        else:
            return 0
            
            
class MainView(FloatLayout):
    mml = ObjectProperty()
    scrolla = ObjectProperty()
    mmbox = ObjectProperty()
    raw_label_text = ""    
    
    def read_map_from_file(self,filename):
        tree = etree.parse(filename)
        self.rootnode = tree.getroot()
        self.raw_label_text = ""
        self.firstnode = self.rootnode.find("node")
        self.firstnode.set("FOLDED","False")
        self.raw_label_text = self.parse_node_to_text(self.firstnode,0,"")
        return self.raw_label_text
        
    def parse_node_to_text(self,node,level,outstr):    
        if node.tag=="node":
            newnode=Node()
            firstnodepos = [self.pos[0], self.size[1]]
            newnode.create_itself(node,self.scrolla,firstnodepos)
            
            self.add_widget(newnode)
        else:
            print "what?", node.tag
        return outstr    
    
    def nodepress(self,instance,value):
        print "press , ", value
        node = self.rootnode.xpath("//node[@ID='" + value + "']")[0]
        #print node
        if (node.get("FOLDED")=="False"):
            node.set("FOLDED","True")
        else:
            node.set("FOLDED","False")
        
        self.raw_label_text = self.parse_node_to_text(self.rootnode.find("node"),0,"")
        self.mml.text=self.raw_label_text   
        self.mml.texture_update()
    
    
    def filllabel(self):
        print "bla"
        self.mml.text = self.read_map_from_file("test3.mm")
        self.mml.bind(on_ref_press=self.nodepress)
        self.mml.markup=True

class mmviewApp(App):

    def build(self):
        mv = MainView()
        mv.filllabel()
        return mv

if __name__ == '__main__':
    mmviewApp().run()