from colorama import Fore,Back

class ErrorHandler:
    """ ErrorHandler for registering and querying all sorts of errors during compilation """
    def __init__(self):
        super().__init__()
        self.warnings = []
        self.errors = []
        self.fatals = []
        self.idx = {}

    class error_iter:
        def __init__(self,ehandler):
            self.values=sorted(ehandler.idx.keys())
            self.ehandler=ehandler

        def __iter__(self):
            return self

        def __next__(self):
            if len(self.values)==0:
                raise StopIteration()
            else:
                value = self.values[0]
                self.values=self.values[1:]
                return (self.ehandler.idx[value])

    def __iter__(self):
        eiter = self.error_iter(self)
        return eiter


    def registerWarning(self,filename, line, col, message):
        warning = (filename,line,col,message)
        self.warnings.append(warning)
        self.idx[(warning[1],warning[2])]=warning

    def countWarnings(self):
        return len(self.warnings)

    def registerError(self,filename, line, col, message):
        error = (filename,line,col,message)
        self.errors.append(error)
        self.idx[(error[1],error[2])]=error
    
    def countErrors(self):
        return len(self.errors)

    def registerFatal(self,filename, line, col, message):
        fatal=(filename,line,col,message)
        self.fatals.append(fatal)
        self.idx[(fatal[1],fatal[2])]=fatal

    def countFatals(self):
        return len(self.fatals)

    def roughlyOk(self):
        return self.countFatals()+self.countErrors()==0

    def cleanCode(self):
        return self.countFatals()+self.countErrors()+self.countWarnings()==0

    def to_explanation(self,input):
        e_iter = iter(self)
        try:
            currenterror = e_iter.__next__()
        except:
            currenterror = ('',0,0,'')
        from src.marm.lexer import marmlexer
        from src.marm.lexer import keywords
        mylexer = marmlexer('',ErrorHandler(),True)
        mylexer.input(input)
        token = mylexer.token()
        output='  1 '
        linecounter=1
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
                while linecounter==currenterror[1]:
                    col=0
                    output+='   '
                    while col<currenterror[2]:
                        col+=1
                        output+=' '
                    output+='^\n   '+Fore.RED+currenterror[3]+Fore.RESET+'\n'
                    try:
                        currenterror=e_iter.__next__()
                    except:
                        break
                      
                linecounter+=len(token.value)
                output+="{:3} ".format(linecounter)
            token = mylexer.token()
        return output


    def tostring(self,color=True):
        retstring = ''
        if color==True:
            formatstring=Back.BLACK+Fore.LIGHTYELLOW_EX+"{}:{}.{}: "+Back.RESET+Fore.RED
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


marmcompiler_stages = ['lex', 'parse', 'analyse_scope', 'typecheck', 'codegen']


def marmcompiler(filename, input, output, errorhandler=None, stages=None):
    from src.marm.parser import marmparser,ParserError
    #yacc = yacc.yacc()
    if stages is None:
        stages = ['parse', 'analyse_scope', 'typecheck']
    if errorhandler is None:
        errorhandler = ErrorHandler()

    completed_stages=[]
    result = None
    for stage in stages:
        if stage == 'lex':
            from src.marm.lexer import marmlexer
            result = marmlexer(filename, input, errorhandler)
        elif stage == 'parse':
            from src.marm.parser import marmparser, ParserError
            try:
                result = marmparser(filename, input, errorhandler)
            except ParserError as err:
                print(err)
        elif stage == 'analyse_scope':
            assert('parse' in completed_stages)
            result.analyse_scope([], errorhandler)
        elif stage == 'typecheck':
            assert('analyse_scope' in completed_stages)
            result.typecheck(errorhandler)
        elif stage == 'codegen':
            assert('typecheck' in completed_stages)
            code = result.code_gen_with_labels(0)
            print(code, "\n", file=output, flush=True)

        if errorhandler.roughlyOk():
            completed_stages.append(stage)
        else:
#            print(coloring(input))
            print(errorhandler.tostring())
            print(errorhandler.to_explanation(input))
            print("Errors occured during {}.".format(stage))
            return None

 #   print(coloring(input))
    print(errorhandler.tostring())
    print(errorhandler.to_explanation(input))

    return result

def coloring(input):
    from src.marm.lexer import marmlexer
    from src.marm.lexer import keywords
    mylexer = marmlexer('',ErrorHandler(),True)
    mylexer.input(input)
    token = mylexer.token()
    output='  1 '
    linecounter=1
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
            linecounter+=len(token.value)
            output+="{:3} ".format(linecounter)
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
    parser.add_argument('--output-format',
                        choices=['json', 'str', 'list_str'],
                        default='json',
                        help="Format used for output. Defaults to json")
    parser.add_argument('--stages', choices=marmcompiler_stages,
                        nargs='*', default=None,
                        help="Compiler stages to be run, in order. Defaults to all.")
    args = parser.parse_args()

    myinput = args.input.read()

    result = marmcompiler(args.input.name, myinput, args.output, None, args.stages)

    if result is None:
        print("No result produced.")
        exit(1)
    else:
        if args.output_format == 'json':
            import json
            args.output.write(result.toJSON())
        elif args.output_format == 'str':
            args.output.write(str(result))
        elif args.output_format == 'list_str':
            for el in result:
                args.output.write(str(el))
                args.output.write("\n")
        else:
            print("Unknown output format {}.".format(args.output_format))
