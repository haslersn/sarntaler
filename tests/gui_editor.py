from src.marm.lexer import marmlexer_minimal,keywords
from tkinter import *
import sys, os

class easyTex(Text):
    def __init__(self,base,**args):
        Text.__init__(self,base,**args)
        self.tag_configure("default",    foreground="black")
        self.tag_configure("INTCONST",  foreground="red")
        self.tag_configure("keywords",   foreground="blue")
        self.tag_configure("COMMENT",    foreground="green")
        self.tag_configure("IDENT", foreground="brown")

    def highlightMarm(self):
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

base = Tk()
editor = easyTex(base)

base.bind("<Escape>", lambda e: sys.exit())
base.bind("<Key>", lambda e: editor.highlightMarm())

editor.pack(fill=BOTH, expand=1)

base.call('wm', 'attributes', '.', '-topmost', True)
mainloop()