
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
    bgcolor = ListProperty([.25,0.25,0.25])
    
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
                self.rootwidget.rebuild_map()
            
    def fold(self):
        print "fold:  ", self.text
        self.folded = True
        self.xmlnode.set("FOLDED","True")
    
    def unfold(self):
        print "unfold, "
        self.folded = False
        self.xmlnode.set("FOLDED","False")
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
            has_open_children = False
            if xmlnode.get("FOLDED",default="False")=="False" or unfold==True:
                xmlnode.set("FOLDED","False")
                self.folded=False
                for nodechild in xmlnode:
                    if nodechild.tag=="node":
                        has_open_children=True
                        #print "childnode... ", childpos, self.pos, "--",self.size
                        newnode = Node()
                        #childpos=(childpos[0],childpos[1])
                        childboxy = newnode.create_itself(nodechild,rootwidget,childpos)
                        rootwidget.add_widget(newnode)
                        #self.add_widget(newnode)
                        self.childnodes.append(newnode)
                        childpos[1]  += childboxy
                        self.bbox[1] += childboxy
                if has_open_children:
                    
                    print "has open children, ", self.text
                    self.bbox[1] -=childboxy
                    
            else:
                self.folded = True
                print "folded: ",self.text,xmlnode.find("node")
                print(etree.tostring(self.xmlnode, pretty_print=True))
                if xmlnode.find("node") !=None:
                    print " has folded kids", self.text
                    self.bgcolor = [.4,0.4,0.4]
                    self.canvas.ask_update()
            #self.size = [self.nwidth,self.nheight]
            
            return self.bbox[1]
        else:
            return 0
            
            
class MainView(FloatLayout):
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
        newnode.create_itself(self.firstnode,self,firstnodepos)
        self.add_widget(newnode)
        
    def build_map(self,node,level,outstr):    
        if node.tag=="node":
            newnode=Node()
            firstnodepos = [0,0]
            newnode.create_itself(node,self,firstnodepos)
            self.add_widget(newnode)
        else:
            print "what?", node.tag
        return outstr    

        
class mmviewApp(App):

    def build(self):
        mv = MainView()
        mv.read_map_from_file("test3.mm")
        return mv

if __name__ == '__main__':
    mmviewApp().run()