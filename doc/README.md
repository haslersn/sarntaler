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
	`123
	0x41324
	add
	"hallo"
	0x1111111
	stores`

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
| OP_ADD |s_1 and s_2 integers | consumes the two highest stack cells and pushes s_2 + s_1 |
| OP_SUB |s_1 and s_2 integers | consumes the two highest stack cells and pushes s_2 - s_1 |
| OP_MUL |s_1 and s_2 integers | consumes the two highest stack cells and pushes s_2 * s_1 |
| OP_DIV |s_1 and s_2 integers | consumes the two highest stack cells and pushes s_2 / s_1 |
| OP_MOD |s_1 and s_2 integers | consumes the two highest stack cells and pushes s_2 % s_1 |
| OP_AND |s_1 and s_2 integers | consumes the two highest stack cells and pushes s_2 & s_1 |
| OP_OR | s_1 and s_2 integers| consumes the two highest stack cells and pushes s_2 \| s_1 |
| OP_XOR |s_1 and s_2 integers | consumes the two highest stack cells and pushes s_2 ^ s_1 |
| OP_EQU | - | consumes the two highest stack cells and pushes s_2 = s_1 |
| OP_LE |s_1 and s_2 integers | consumes the two highest stack cells and pushes s_2 <= s_1 |
| OP_GE |s_1 and s_2 integers | consumes the two highest stack cells and pushes s_2 >= s_1 |
| OP_NEG |s_1 integer | consumes the highest stack cell and pushes -s_1 |
| OP_NOT |s_1 integer | consumes the highest stack cell and pushes 1 - s_1 |
| OP_JUMP | s_1 integer and line exists | absolute jump, consumes highest stack cell, PC = s_1 |
| OP_JUMPR | s_1 integer and boundaries are kept | consumes highest stack cell, PC = s_1 + PC |
| OP_JUMPC | s_1 integer and s_2 integer and line s_2 exists| absolute conditional Jump. Consumes 2 Arguments. If s_1 == 1, PC = s_2 else nothing happens | 
| OP_JUMPRC | s_1 integer and s_2 integer and line s_2 keeps boundaries | relative conditional Jump. Consumes 2 Arguments. If s_1 == 1, PC = PC + s_2 else nothing happens | 
| OP_SWAP | | Swaps s_1 and s_2|
| OP_DUP |- | pushes s_1 |
| OP_PUSHABS |- | consumes the highest stack cell. Let n be its value. It pushes the n-th cell of the stack. The lowest stack cell has index 0, the next one 1 and so on. |
| OP_PUSHFP |- | pushes the FramePointer |
| OP_PUSHSP |- | pushes the StackPointer |
| OP_POPFP |- | pops into the FramePointer |
| OP_POPSP |- | pops into the StackPointer |
| OP_PUSHPC | - | pushes the Program Counter |


