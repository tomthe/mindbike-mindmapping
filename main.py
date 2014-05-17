
import kivy
from kivy.uix.modalview import ModalView
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty, StringProperty,ObjectProperty
from kivy.app import App
from readmm import stringize

kivy.require('1.0.7')


class ColorView(ModalView):
    bcolour = ListProperty([0.5,0.5,0.5,1])
    answer_text = StringProperty('')
    font_size = StringProperty('50dp')
    
class MainView(BoxLayout):
    mml = ObjectProperty()
    
    def filllabel(self):
       self.mml.text = stringize("testtemp.mm")

class mmviewApp(App):

    def build(self):
        mv = MainView()
        mv.filllabel()
        return mv

if __name__ == '__main__':
    mmviewApp().run()