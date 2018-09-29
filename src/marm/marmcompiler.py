from colorama import Fore,Back

class ErrorHandler:
    """ ErrorHandler for registering and querying all sorts of errors during compilation """
    def __init__(self):
        super().__init__()
        self.warnings = []
        self.errors = []
        self.fatals = []

    def registerWarning(self,filename, line, col, message):
        self.warnings.append((filename,line,col,message))

    def countWarnings(self):
        return len(self.warnings)

    def registerError(self,filename, line, col, message):
        self.errors.append((filename,line,col,message))
    
    def countErrors(self):
        return len(self.errors)
    
    def registerFatal(self,filename, line, col, message):
        self.fatals.append((filename,line,col,message))

    def countFatals(self):
        return len(self.fatals)

    def roughlyOk(self):
        return self.countFatals()+self.countErrors()==0

    def cleanCode(self):
        return self.countFatals()+self.countErrors()+self.countWarnings()==0

    def tostring(self,color=True):
        retstring = ''
        if color==True:
            formatstring=Fore.LIGHTYELLOW_EX+"{}:{}.{}: "+Fore.RED
        else:
            formatstring="{}:{}.{}: "
        for f in self.fatals:
            retstring += (formatstring+"{}\n").format( f[0], f[1], f[2], f[3] )
        for e in self.errors:
            retstring += (formatstring+"{}\n").format( e[0], e[1], e[2], e[3] )
        for w in self.warnings :
            retstring += (formatstring+"{}\n").format( w[0], w[1], w[2], w[3] )
        if color==True:
            retstring+=Fore.RESET
        return retstring
    def __str__(self):
        return self.tostring(False)

def marmcompiler(filename, input, errorhandler=None):
    from src.marm.parser import marmparser,ParserError
    #yacc = yacc.yacc()
    result=None
    if errorhandler is None:
        errorhandler = ErrorHandler()
    try:
        result = marmparser(filename,input,errorhandler)
    except ParserError as err:
        print(err)
    print(errorhandler.tostring())
    #result.analyse_scope()
    return result

def coloring(input):
    from src.marm.lexer import marmlexer
    from src.marm.lexer import keywords
    mylexer = marmlexer('',ErrorHandler(),True)
    mylexer.input(input)
    token = mylexer.token()
    output='  1 '
    linecounter=2
    while not (token is None):
        if token.type=='IDENT':
            output+=Fore.YELLOW 
        if token.type=='INTCONST':
            output+=Fore.RED 
        if token.type=='COMMENT':
            output+=Fore.GREEN
        if token.type in keywords.values():
            output+=Fore.CYAN
        output+= str(token.value)+Fore.RESET
        if token.type=='NEWLINE':
            output+="{:3} ".format(linecounter)
            linecounter+=1
        token = mylexer.token()
    return output

if __name__ == "__main__":
    # Parse Arguments
    import sys
    import argparse
    parser = argparse.ArgumentParser(description='Parse the given file')
    parser.add_argument('--input', type=argparse.FileType('r'), default=sys.stdin,
                        help="Input file. Defaults to stdin")
    parser.add_argument('--output', type=argparse.FileType('w'), default=sys.stdout,
                        help="Output file. Defaults to stdout")
    parser.add_argument('--output-format', choices=['json', 'str'], default='json',
                        help="Format used for output. Defaults to json")
    args = parser.parse_args()
    myinput = args.input.read()
    result=coloring(myinput)
    print(result)
    result = marmcompiler(args.input.name,myinput)
    if result is not None:
        if args.output_format == 'json':
            args.output.write(result.toJSON())
        elif args.output_format == 'str':
            args.output.write(str(result))
        else:
            print("Unknown output format {}.".format(args.output_format))
