# -*- coding: utf-8 -*-
"""
Created on Sat May 17 02:02:43 2014

@author: tom
"""

#mindmap 2 labeltext:

from lxml import etree



def printnode(node,level,outstr):
    
    if node.tag=="node":
        #print " " * level, level, node.get("TEXT"), node.tag
        outstr += "    " * level + "[ref=" + node.get("ID") + "]" +  node.get("TEXT") +"[/ref]"+ chr(10)
        for nodechild in node:
            if nodechild.tag=="node":
                #print "gugu1, ",nodechild.tag
                outstr = printnode(nodechild,level+1,outstr)
    else:
        print "what?", node.tag
            
    return outstr
        
def stringize(filename):
    
    outstr=""
    
    tree = etree.parse(filename)
    root = tree.getroot()
    print"blabla"
    
    for child in root:
        if child.tag=="node":
            outstr = printnode(child,0,outstr)
    
    print outstr
    return outstr

#stringize("testtemp.mm")