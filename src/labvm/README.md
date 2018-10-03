# labVM Documentation

## Basics
The labVM is a stack-based Virtual Machine. The Stack can hold references to either Integer or Strings of arbitrary size.

## Registers and Data Structures
 PC, FP, SP

 Stack, Storage

## Syntax
The syntax of labVM Script is very simple. A labVM script consist of two kind of elements each seperated by a newline: data and machine instructions. Empty lines will be ignored.

Strings are outlined with quote-characters. These can either be single quotes or double quotes, as long as they match each other.

*Example:*
	"Hello World"
and
	'Hello World'
are both equivalent.

For Integers, do not use quotes. The number will then be interpreted as a decimal integer. Use a 0x-Prefix for hexadeuse quotes. The number will then be interpreted as a decimal integer. Use a 0x-Prefix for hexadecimal. Do not use trailing zeros except for the value zero itself.

If you want to use special characters like a new line, use the usual escape sequences (i.e. \n).


For Instructions, just write the name of the instruction. The interpreter is case-insensitive. For a list of all instructions see Section XX.

Comments can be added with leading //. They work inline and as an extra line but if they are on an extra line they don't get counted to the codelines you need to specify jumps. So inline comments should be preferred.

For inline comments there has to be whitespace before the comment!

*Example:*

	OP_ADD //this adds two stack elements
works, but

	OP_ADD//this adds two stack elements
doesn't work.

Example Program:

	123
	0x41324
	op_add
	0x1111111
	OP_ADD
	OP_RET

## Instructions
remark: For the highest element on the stack **before the execution** s_1, for the second highest s_2, and so on:

|       |
| ----- |
|  s_1  |
|  s_2  |
|  ...  |
|  s_n  |

The stack grows to the top in this figure.

**Stack Layout**
When a contract is started, the Stack is initialised with the following parameters:

|  |
| -- |
|  -1  |
| -1 | <- FP
| par 1 |
| ... |
| par n |
| money spent on current call : int |
| caller addresses : List(Hash) |
| own account address : Hash |

For testing the amounts of elements, push the FP and subtract 3.
The only valid way to exit the program is by using a OP_RET on the last stack frame (the one in the picture)


Boolean values are ints. 1 represents true and 0 represents false.


|Instruction | Constraints | Description |
| ---------- | ----------- | ----------- |
|_**Math**_|
| OP_ADD |s_1 and s_2 integers | consumes the two highest stack cells and pushes s_2 + s_1 |
| OP_SUB |s_1 and s_2 integers | consumes the two highest stack cells and pushes s_2 - s_1 |
| OP_MUL |s_1 and s_2 integers | consumes the two highest stack cells and pushes s_2 * s_1 |
| OP_DIV |s_1 and s_2 integers | consumes the two highest stack cells and pushes s_2 / s_1 |
| OP_MOD |s_1 and s_2 integers | consumes the two highest stack cells and pushes s_2 % s_1 |
| OP_AND |s_1 and s_2 integers | consumes the two highest stack cells and pushes s_2 & s_1 |
| OP_OR | s_1 and s_2 integers| consumes the two highest stack cells and pushes s_2 \| s_1 |
| OP_XOR |s_1 and s_2 integers | consumes the two highest stack cells and pushes s_2 ^ s_1 |
|_**Comparison**_|
| OP_EQU | - | consumes the two highest stack cells and pushes s_2 = s_1 |
| OP_LE |s_1 and s_2 integers | consumes the two highest stack cells and pushes s_2 <= s_1 |
| OP_GE |s_1 and s_2 integers | consumes the two highest stack cells and pushes s_2 >= s_1 |
| OP_LT |s_1 and s_2 integers | consumes the two highest stack cells and pushes s_2 < s_1 |
| OP_GT |s_1 and s_2 integers | consumes the two highest stack cells and pushes s_2 > s_1 |
| OP_NEG |s_1 integer | consumes the highest stack cell and pushes -s_1 |
| OP_NOT |s_1 integer | consumes the highest stack cell and pushes 1 - s_1 |
|_**Flow Control**_|
| OP_JUMP | s_1 integer and line exists | absolute jump, consumes highest stack cell, PC = s_1 |
| OP_JUMPR | s_1 integer and boundaries are kept | consumes highest stack cell, PC = s_1 + PC |
| OP_JUMPC | s_1 integer and s_2 integer and line s_1 exists| absolute conditional Jump. Consumes 2 Arguments. If s_2 == 1, PC = s_1 else nothing happens |
| OP_JUMPRC | s_1 integer and s_2 integer and line s_1 keeps boundaries | relative conditional Jump. Consumes 2 Arguments. If s_2 == 1, PC = PC + s_1 else nothing happens |
| OP_CALL | s_1 valid code line | consumes s_1, pushes FP, sets FP = SP (points to old FP, pushes PC (return address), jumps |
| OP_RET | needs a valid stack frame | s_1 will be interpreted as the return value. restores FP and PC, everything on the stack between the return address and the return value gets lost, if oldfp == -1, stop contract and return highest stack cell |
| OP_KILL | - | kills execution with an error |
|_**Stack**_|
| OP_SWAP | | Swaps s_1 and s_2|
| OP_DUP |- | pushes s_1 |
| OP_PUSHABS | s_1 valid stack index | consumes the highest stack cell. Let n be its value. It pushes the n-th cell of the stack. The lowest stack cell has index 0, the next one 1 and so on. |
| OP_POPABS  | s_1 valid stack index | consumes the two highest stack cells. Stores s_2 at the absolute stack index s_1 |
| OP_PUSHFP |- | pushes the FramePointer |
| OP_POPFP | s_1 non-negative integer or -1 | pops into the FramePointer |
| OP_PUSHSP |- | pushes the StackPointer |
| OP_POPSP | s_1 non-negative integer or -1 | pops into the StackPointer |
| OP_PUSHPC | - | pushes the Program Counter |
| OP_POPPC | s_1 valid code line | pop into the Program Counter |
| OP_POPVOID | stack not empty | removes s_1 |
|_**String**_|
| OP_PACK | s_1 integer, at least s_1 +1 stack elements | Packs the number of stack elements given in s_1 into a single string separated by spaces, starting from s_2 and consuming them all. The topmost stack element will be the last element in the string. Pushes the resulting String onto the stack. The resulting string can be used e.g. to pass parameters to OP_TRANSFER. Reverse operation: OP_UNPACK
| OP_UNPACK | s_1 string | Splits the string at s_1 by spaces and pushes the parts onto the stack in the order they appear in the string (i.e. the first element of the string will be furthest down on the stack). Also leaves the number of elements that were pushed in s_1 (excluding s_1 itself). Reverse operation: OP_PACK
|_**Blockchain**_|
| OP_GETBAL | s_1 hash | Puts the account balance of the account at address s_1 (which is the hash of the public key) on the stack. If no account is at address s_1, then **-1** is put on the stack.|
| OP_GETOWNBAL | - | Puts the account balance of the own account on the stack.|
| OP_GETSTOR | s_1 string | Consumes s_1 and leaves the value of the storage cell referenced by s_1 on the stack. |
| OP_SETSTOR | s_2 string | Consumes s_1 and s_2 and stores the value of s_2 in the storage cell referenced by s_1. |
| OP_TRANSFER | s_1 integer, s_2 hash, s_3 list[string] | Consumes s_1 to s_3 and calls the contract at address s_2 (which is a hash of the public key) with the parameters stored in s_3, sending the amount of money specified in s_1. Leaves a success code at s_1 and return value at s_2. The amount of money may be zero but not negative and the parameters may be empty. |
| OP_CREATECONTR | s_1 pubkey, s_2 string, s_3 boolean, s_4 list[string], s_5 list | Consumes s_1 to s_5 and creates a new account with public key in s_1, contract code in s_2, owner_access flag in s_3. s_4 and s_5 are lists of storage variable names and their initial values, respectively. Leaves a 1 on the stack if the contract creation succeeded, 0 otherwise. |


Lines are numbered beginning with 1 and empty lines are not counted

# Macros
Macros that are implemented:

`OP_PUSHR` (Push relative to FP) is equal to `OP_PUSHFP, OP_ADD, OP_PUSHABS`

`OP_POPR` (Store relative to FP) is equal to `OP_PUSHFP, OP_ADD, OP_POPABS`

`OP_INCFP` (In-/Decrement FP) is equal to `OP_PUSHFP, OP_ADD, OP_POPFP`

# Examples
## GCD


	0
	op_pushabs
	1
	op_pushabs			// load both variables on the stack
	op_equ
	26
	op_jumprc			// if equal, jump to end
	0
	op_pushabs
	1
	op_pushabs
	op_le
	10
	op_jumprc			// if a <= b goto else part
	0				// beginning of if part
	op_pushabs
	1
	op_pushabs
	op_sub				// a - b
	0
	op_popabs			// store in a
	8				// jump to end of if then else
	op_jumpr
	1				// beginning of else part
	op_pushabs
	0
	op_pushabs
	op_sub				// b - a
	1
	op_popabs			// store in b
	-31
	op_jumpr			// jump back to while condition

*Explanation:* This Code computes the gcd of two numbers already in the first two stack cells. It is based on the Euclid's algorithm:

	bool gcd(int a, int b) {
	    while(a != b) {
	        if(a > b) {
	            a = a - b;
	        } else {
	            b = b - a;
	        }
	    }
	    return a;
	}

## Factorial

    21              // Line 21 is the start of the main-method
    OP_JUMP         // Jump to the main-method
    -1
    OP_PUSHR        // -1 OP_PUSHR gets the parameter that was put on the stack before calling the function
    1
    OP_GT           // check if parameter >= 1
    11
    OP_JUMPC        // if parameter >= 1 is true, jump to line 11
    1
    OP_RET          // parameter >= 1 is false, put on the stack as returnvalue and return
    -1
    OP_PUSHR        // get the parameter again
    1
    OP_SUB          // subtract 1 from the parameter
    3
    OP_CALL         // call fac on line 3 again with the decremented parameter
    -1
    OP_PUSHR        // get the paramter again
    OP_MUL          // muliply parameter and fac(parameter-1)
    OP_RET          // return the result of the multiplication
    10              // put the value that we want the factorial of on the stack
    3               // Line 3 is the start of the fac() method
    OP_CALL         // call fac-method
    3628800         // the value of fac(10)
    OP_EQU          // check if our calculation was right
