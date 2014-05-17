# -*- coding: utf-8 -*-
"""
Created on Sat May 17 02:02:43 2014

@author: tom
"""

#mindmap 2 labeltext:

from lxml import etree



def printnode(node,level,outstr):
    
    if node.tag=="node":
        level += 1
        print " " * level, level, node.get("TEXT"), node.tag
        outstr += "    " * level + node.get("TEXT") + chr(10)
        for nodechild in node:
            if nodechild.tag=="node":
                #print "gugu1, ",nodechild.tag
                outstr = printnode(nodechild,level,outstr)
    else:
        print "what?", node.tag
            
    return outstr
        
def stringize(filename):
    
    outstr="a"
    
    tree = etree.parse(filename)
    root = tree.getroot()
    print"blabla"
    
    for child in root:
        if child.tag=="node":
            print "gugu0, ",child.tag
            outstr = printnode(child,0,outstr)
    
    print outstr
    return outstr

#stringize("C:\dev\python\mindmapviewer/testtemp.mm")