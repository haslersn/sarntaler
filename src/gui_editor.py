from src.marm.lexer import marmlexer_minimal,keywords
from tkinter import *
import sys, os

class SyntaxHiglighterMarm(Text):
    def __init__(self,base,**args):
        Text.__init__(self,base,**args)
        self.tag_configure("default",    foreground="black")
        self.tag_configure("INTCONST",  foreground="red")
        self.tag_configure("keywords",   foreground="blue")
        self.tag_configure("COMMENT",    foreground="green")
        self.tag_configure("IDENT", foreground="brown")
        self.bind("<Key>", self.highlightMarm)
        self.bind("<Control-v>", lambda arg:self.preparePaste(arg, base))

    def highlightMarm(self, key):
        if key.keysym == "Tab":
            return "break"
        self.tag_remove("INTCONST", "1.0", "end")
        self.tag_remove("IDENT", "1.0", "end")
        self.tag_remove("COMMENT", "1.0", "end")
        self.tag_remove("keywords", "1.0", "end")

        from src.marm.lexer import marmlexer_minimal
        mylexer = marmlexer_minimal()
        input=self.get(1.0,"end")
        mylexer.input(input)
        print(input)
        linecounter=1
        colcounter=0
        tagstack=[]
        while True:
            token = mylexer.token()
            if token is None:
                break
            # token matching
            if token.type=='NEWLINE':
                linecounter+=len(token.value)
                colcounter=-1
            tag=''
            if token.type in keywords.values():
                tag='keywords'
            if token.type=='IDENT' or token.type=="INTCONST" or token.type=='COMMENT':
                tag=token.type
            length=len(str(token.value))
            if len(tag)>0:
                tagstack.append((tag,"%s.%s" %(linecounter,colcounter),"%s.%s"%(linecounter,colcounter+length)))
            colcounter+=length
        tagstack.reverse()
        for mytag in tagstack:
            self.tag_add(mytag[0],mytag[1],mytag[2])
        print('done')
        
    def preparePaste(self, key, master):
        try:
            str = master.clipboard_get()
            master.clipboard_clear()
            master.clipboard_append(str.replace("\t", " "))
        except TclError:
            return 