# labVM Documentation 

## Basics
The labVM is a stack-based Virtual Machine. The Stack can hold references to either Integer or Strings of arbitrary size.

## Registers and Data Structures
 PC, FP, SP
 Stack(, Memory?)

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

Example Program:

	123
	0x41324
	op_add
	"hallo"
	0x1111111
	OP_ADD

## Instructions
remark: For the highest element on the stack **before the execution** s_1, for the second highest s_2, and so on:

|       |
| ----- |
|  s_1  |
|  s_2  |
|  ...  |
|  s_n  |

The stack grows to the top in this figure.

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
| OP_RET | needs a valid stack frame | DO NOT USE OP_RETURN! s_1 will be interpreted as the return value. restores FP and PC, everything on the stack between the return address and the return value gets lost |
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

# Macros
Macros that are implemented:

`OP_PUSHR` (Push relative to FP) is equal to `OP_PUSHFP,OP_ADD,OP_PUSHABS`

`OP_POPR` (Store relative to FP) is equal to `OP_PUSHFP,OP_ADD,OP_POPABS`

`OP_INCFP` (In-/Decrement FP) is equal to `OP_PUSHFP, OP_ADD, OP_POPFP`

# Examples


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

Note: The comments are just for explaination. Right now, labVM script does not support comments.

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
