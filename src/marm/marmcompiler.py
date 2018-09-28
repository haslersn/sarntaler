
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

    def __str__(self):
        retstring = ''
        for f in self.fatals:
            retstring += "{}:{}.{}: {}\n".format( f[0], f[1], f[2], f[3] )
        for e in self.errors:
            retstring += "{}:{}.{}: {}\n".format( e[0], e[1], e[2], e[3] )
        for w in self.warnings :
            retstring += "{}:{}.{}: {}\n".format( w[0], w[1], w[2], w[3] )
        return retstring

def marmcompiler(filename, input, errorhandler=None):
    from src.marm.parser import marmparser,ParserError
    #yacc = yacc.yacc()
    if errorhandler is None:
        errorhandler = ErrorHandler()
    try:
        result = marmparser(filename,input,errorhandler)
    except ParserError as err:
        print(err)
    print(errorhandler)
    if errorhandler.roughlyOk():
        result.analyse_scope()
    return result


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
    result = marmcompiler(args.input.name,args.input.read())
    if result is not None:
        if args.output_format == 'json':
            args.output.write(result.toJSON())
        elif args.output_format == 'str':
            args.output.write(str(result))
        else:
            print("Unknown output format {}.".format(args.output_format))
