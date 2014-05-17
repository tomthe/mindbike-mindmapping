
import kivy
from kivy.uix.modalview import ModalView
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty, StringProperty,ObjectProperty
from kivy.app import App
#from readmm import stringize
from lxml import etree


kivy.require('1.0.7')


class ColorView(ModalView):
    bcolour = ListProperty([0.5,0.5,0.5,1])
    answer_text = StringProperty('')
    font_size = StringProperty('50dp')
    
class MainView(BoxLayout):
    mml = ObjectProperty()
    raw_label_text = ""
    
    
    def read_map_from_file(self,filename):
        tree = etree.parse(filename)
        self.rootnode = tree.getroot()
        self.raw_label_text = ""
        self.raw_label_text = self.parse_node_to_text(self.rootnode.find("node"),0,"")
        return self.raw_label_text
        
    def parse_node_to_text(self,node,level,outstr):    
        if node.tag=="node":
            #print " " * level, level, node.get("TEXT"), node.tag
            outstr += "    " * level + "[ref=" + node.get("ID") + "]" +  node.get("TEXT") +"[/ref]"+ chr(10)
            for nodechild in node:
                if nodechild.tag=="node":
                    #print "gugu1, ",nodechild.tag
                    outstr = self.parse_node_to_text(nodechild,level+1,outstr)
        else:
            print "what?", node.tag
                
        return outstr    
    
    def nodepress(self,instance,value):
        print "press , ", value
    
    def filllabel(self):
        print "bla"
        self.mml.text = self.read_map_from_file("testtemp.mm")
        self.mml.bind(on_ref_press=self.nodepress)
 #       self.mml.on_ref_press(self.nodepress)
        self.mml.markup=True

class mmviewApp(App):

    def build(self):
        mv = MainView()
        mv.filllabel()
        return mv

if __name__ == '__main__':
    mmviewApp().run()