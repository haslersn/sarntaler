# marm compiler documentation

## Basics

The marm compiler translates a high level specification similar but not identical
to C into labvm code. It is a PLY-generated compiler, consisting of the usual
lexer, parser, typechecking and code generation phases.

## Syntax
marm is a much more simplified subset of C, but contains special instructions for 
the blockchain. Currently the features include:

- [while loops](#loops)
- [comments](#comments)
- [if branches](#ifs)
- [function calls](#functions)
- [expression statements](#expressions)
- [declaration statements](#declarations) and
- [procedure declarations](#procedures).

### General definition and keywords

#### <a name="head1234"></a> Types
MARM currently supports only integers and sarns as well as addresses.

#### <a name="identifier"></a> Identifiers
Identifiers **must** start with a letter (either lower of larger case) followed by any number 
of number literals or letters or underscores.

#### <a name="keywords"></a> Reserved Keywords
The following words are **reserved keywords** and may not be used in any way. You might use them as
parts of identifiers but not as sole words separated by whitespaces or tabs.

| | | Schlüsselwörter | | |
|:-------------:|:-------------:|:-------------:|:-------------:|:-------------:|
| `if` | `while` | `break` | `continue` | `else` | 
| `return` | `int` | `address` | `sarn` | `msg` |
| | |`contract` | | |


### <a name="comments"></a> Comments

We support both in-line and multi-line comments. The syntax is directly inherited by C:
```c 
statement; //This is a comment that includes everything after the two slashes (//) until the end of the line is reached.
This is *not* a comment
/* This is a multi-line comment. 
So this line is basically still in the comment.
It starts with a slash following a star (/*) and ends 
with a star followed by a slash */
```
The regular expression for comments is defined by
```bnf
(\/\*([^*]|\* + [^*\/])*\*+\/)|(\/\/[^\r\n]*)
```
, but is ignored by the lexer. So every content there is inside a comment is completely
disregarded. 

### <a name="declarations"></a> Declaration statements

You can declare variables with a type followed by a list of identifiers. It **must** end with 
a semicolon (`;`):
```c
<type> identifier;
<type> ident1, ident2, ...;
```

The grammar for variable declarations is defined by
```bnf
statement : type decllist SEMI

decllist  : decl COMMA decllist
          | decl

decl      : IDENT
```

<aside class="warning"> <span style="color:red">
Until now you <b>must not</b> include variable declarations outside of procedures. It <b>will</b> be implemented
in the future but right now it will result in an error! </span>
</aside>


### <a name="procedures"></a> Procedure declarations

Basically you would define a procedure as you would in C. So
```c
<type> procedure(paramlist...);
```
as well as
```c
<type> procedure(paramlist...) {
    //statements
}
```
is possible. You can write multiple procedures in one file, but you cannot have multiple procedures
with the same name (in the same file).
Until now you also cannot define a main entry point for the contract, the entry and exit points
are defined by the transactions.
In the code snippets above `<type>` **must** be a type from the [list](#head1234) above, the procedure 
name **cannot** be a reserved keyword and the `paramlist` can include parameter definitions as they are defined 
by
```c
<type> identifier
``` 
where `<type>` also is a type from the [list](#head1234) above and the `identifier` fulfills the rules specified [above](#identifier).
You can have multiple definitions separated by commas.


The grammar for procedure declarations is defined by
```bnf
procdecllist : procdecl procdecllist
             | procdecl
             
procdecl     : type IDENT LPAR paramlistopt RPAR statementlistOPT
```

### <a name="loops"></a> Loop statements
Currently only `while` loops are supported. However, `do while` and `for` loops can easily
be transformed to simple `while` loops:
```c 
...
for(INIT; COND; INCR) {
    //Code executed in every (for) loop pass
}

do {
    //Code executed in every loop pass
} while (COND);
...
```
can be transformed to
```c 
...
INIT;
while(COND) {
    //Code executed in every (for) loop pass
    INCR;
}

//Code executed in every loop pass
while (COND) {
    //Code executed in every loop pass
}
...
```
The grammar for loop statements is definied by
```bnf
statement : WHILE LPAR boolex RPAR statement
```
### <a name="ifs"></a> If branches

### <a name="functions"></a> Function calls

## Example

```c
int main(int param1,int param2){
    int i;
    i = 0;
    while (i<param1) {
        i=i+param2;
    }
    return i;
}
```

## Usage

```python
from src.marm.marmcompiler import marmcompiler, coloring
print(coloring('..... marmcode ......'))
print(marmcompiler('filename','........ marmcode.........'))
```
