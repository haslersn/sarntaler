# MARM compiler documentation

## Basics

The MARM compiler translates a high level specification similar but not identical
to C into labvm code. It is a PLY-generated compiler, consisting of the usual
lexer, parser, typechecking and code generation phases.

## Syntax
MARM is a much more simplified subset of C, but contains special instructions for 
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
MARM currently supports only integers, sarns as well as addresses.
##### Integer types
Variables of type `int` can store any integer number. Examples: 
```c
int example_variable_of_type_int, snd_example_variable_of_type_int;
example_variable_of_type_int = 4020495;
snd_example_variable_of_type_int = -342592834;
``` 
##### Sarns
Variables of type `sarn` can store any **unsigned** integer number and should be used to
store currency values. They include the zero but **cannot** go below! 
```c
sarn value_amount, not_allowed;
value_amount = 4020495; 
not_allowed = -342592834; // This is not allowed and will raise an Exception!
``` 
##### Addresses
Variables of type `address` can store any address (an integer with 32 bytes). They should only
be assigned by calling the specific procedures to create accounts or calling the message sender. 
```c
address a, b;
a = create(value_amount); // value_amount is of type sarn
b = msg.account; // stores the associated account of the message sender in b
``` 

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

### <a name="contractdata"></a> Contract data
At the beginning of every file you can write contract-global variables you later can easily access. 
You can do so by writing a `contract` block that includes many declaration statements for variables. 
For example:
```c
contract {
    //Here follow multiple declarations of variables
    /*
     *  However only the declarations are valid here, 
     *  so you *cannot* define procedures in here.
     */
}
```

The grammar is defined by
```bnf
contractdata : CONTRACT BEGIN contractlist END 
             |
             
contractlist : paramdecl SEMI contractlist
             |
```

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

##### WARNING
<aside class="warning"> 
<span style="color:red">
Until now you <b>must not</b> include variable declarations outside of procedures. It <b>will</b> be implemented
in the future but right now it will result in an error! 
</span>
</aside>


### <a name="expressions"></a> Expression statements
You can define multiple expressions of different types. The types include

- [constant expressions](#constants)
- [arithmetic expressions](#arithmetic)
- [boolean expressions](#boolex) and
- [expressions for accessing variables](#lhs).

Every expression can be nested in parenthesis and thus the operator precedence changed.
The basic grammar is defined by
```bnf
expr   : LPAR expr RPAR
```
#### <a name="constants"></a> Constant expressions
Expressions can be any constants, either from type integer or the specially reserved keywords
`msg` and `contract`. The `contract` keyword here is another one than the keyword for the definition 
of local variables!
The grammar is defined by
```bnf
expr   : INTCONST
       | MSG
       | CONTRACT
```
#### <a name="arithmetic"></a> Arithmetic expressions
There are two different kinds of arithmetic expressions. On the one hand there are so called 
*binary* expressions, where the operator is written in infix notation and there are two explicit
operands, and on the other hand there are *unary* expressions, where the operator is written in
prefix notation and there is only one explicit operand.

Until now the unary expressions are only represented by an operator to negate the value of the operand.
You could as such easily negate an integer value as it was done in the example for integer types.
The binary expressions contain the addition, subtraction, multiplication and division as well as assignments 
to variables. Therefore the following code snippets are valid expressions:
```bnf
int a,b,c,d;

a + b
c = b - d
d = a * (c / d)
a = -20
c = -d
```
The grammar is defined by
```bnf
expr   : expr ASSIGN expr
       | expr MULOP expr
       | expr ADDOP expr
       | expr DIVOP expr
       | expr MODOP expr
       | expr SUBOP expr
       | SUBOP expr
```
#### <a name="boolex"></a> Boolean expressions
Boolean expressions **always** return boolean values (represented by integer values `0`for 
`false` and `1` for `true`). Boolean expressions can also be nested, negated by a prefix `!`, and
 calculated out of boolean expressions with `&&` (logical and) and `||`(logical or) or other expressions
 with compare statements (`==`, `>=`, `<=`, `>`, `<` with the usual meanings).

The grammar is defined by
```bnf
boolex : expr EQ expr
       | expr NEQ expr
       | expr LEQ expr
       | expr GEQ expr
       | expr LT expr
       | expr GT expr
       | boolex OR boolex
       | boolex AND boolex
       | NOT boolex
       | LPAR boolex RPAR
```
#### <a name="lhs"></a> Expressions for accessing variables
You can access variables simply by entering the variable name. If you want to access information which is 
encapsulated by the message sender or is a contract-global variable in a contract, you can do so by firstly
entering `msg` or `contract` and then separated by a `.` (dot) the variable name (or procedure name).

The grammar is defined by
```bnf
expr          : lhsexpression

lhsexpression : IDENT
              | expr DOT IDENT
```
#### <a name="prec"></a> Operator precedence

#TODO

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

Every procedure should always include a return-statement that is reached in every single branch (see also the warning).
You **shall not** return values that are not compatible with the return type of the procedure!
A return-statement looks exactly like it does in C, so for an example you would have
```c 
return expr;
```
where `expr` could be any valid expression, defined by [these rules](#expressions).
The semicolon is as important as it is in every statement, so don't forget it.

#### Warning
One **should always** include *return*-statements for every single branch. The check for existence of these
return-statements is **not yet implemented**, so the user should be aware of that.


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
The conditional statement `COND` must be a boolean expression 
(as defined in [here](#boolex)).

The grammar for loop statements is defined by
```bnf
statement : WHILE LPAR boolex RPAR statement
```
### <a name="ifs"></a> Conditional code execution

Conditional code execution can be achieved with a simple `if-else` expression. The conditional
statement must also be a boolean expression (as defined in [here](#boolex)). In general the syntax should
look like
```c
if (COND) {
    //only executed if COND evaluates to true
} else {
    //only executed otherwise
}
```
The `else` part is *highly optional* and should be left out if the block would be empty.

The grammar for `if`-expressions is defined by
```bnf
statement : IF LPAR boolex RPAR statement elseprod
elseprod  : ELSE statement
```

### <a name="functions"></a> Function calls
There are two types of function calls: Account creation and calling procedures in a contract.
The first type (account creation) is called by `create` and takes only one parameter, the amount of Sarns
the account should initially have.

The second type is called by entering the procedure name (which might include a `msg.` or an identifier
in front of the procedure name)
and takes any number of parameters the procedure defines.

*The parameters can **always** be other procedure calls or any complex expression!*

The grammar for function calls is defined by
```bnf
expr      : lhsexpression LPAR exprlist_opt RPAR
          | CREATE LPAR exprlist_opt RPAR
```
#### Calling Conventions
Usually we use the *right-to-left* calling convention for procedure calls. In other words for an example procedure with
four parameters like
```c
...
test_calling_convention(param1, param2, param3, param4);
```
`param1` is the last and `param4` the first value that is pushed to the stack.

## Examples

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

```c
contract {
	sarn sar;
	int globalx;
}

int test(int x){
	address a, b;
	sarn s; // sarns are nonnegative integers (uint)
	int i;
	i = 0;
	x = 1;
	s = 4711;
	// create takes sarns from the balance and creates an account
	// whose address it returns
	a = create(s); 

	s = contract.sar;
	contract.globalx = x;

	while(i < 1){
		x = x % 2;
		i = i + 1;
	}
	//messages come with an associated account
	msg.account; 
	// a of type address
	a.balance; 
	// the address of contract c
	c.account; 

	// s is sarn, a is address, a receives s sarns from contracts balance
	a.transfer(s);
	// call contract a's method with name 'method', paying with s sarns 
	// from the this contracts and the params 1 and x
	a.method(s,1,x);
	s = test2(s, a.methodReturnsBoolean(contract.sar, contract.globalx))
	
	b = create(s);
	return x;
}

sarn test2(sarn s, int b) {
    //Do something with s
    sarn n;
    if(b == 1) {
        n = s + 5;
    } else {
        n = s - 5;
    }
    
    return n;
}
```

## Usage

```python
from src.marm.marmcompiler import marmcompiler, coloring
print(coloring('..... marmcode ......'))
print(marmcompiler('filename','........ marmcode.........'))
```
