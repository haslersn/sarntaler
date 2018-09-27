class Translationunit(Node):
    def __init__(self,procdecl):
        self.proc=procdecl
class Procdecl(Node):
    def __init__(self,returnType,name,params,body):
        self.returnType = returnType
        self.name = name
        self.params = params
        self.body = body
