<!--.. blockchain documentation master file, created by
   sphinx-quickstart on Mon Mar  6 15:54:51 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to labChain's documentation!
======================================

This project is a completely new blockchain-based coin, with P2P networking, a consensus mechanism and a wallet interface. The goal of the project is to provide a framework that is easy to modify for people who want to develop proof-of-concepts for blockchain-based technology.

DO NOT USE THIS AS A REAL CURRENCY TO SEND, RETRIEVE, OR STORE ACTUAL MONEY! While we do not currently know of any way to do so, there are almost certainly
bugs in this implementation that would allow anyone to create money out of the blue or take yours away from you.


Executables
***********

.. list-table::
    :stub-columns: 1
    :widths: 10 90

    * - miner
      - .. automodule:: miner
    * - wallet
      - .. automodule:: wallet

To start a minimal network of two peers that do not mine, you can do this on different machines::

    ./miner.py --listen-port 1234
    ./miner.py --bootstrap-peer a.b.c.d:1234

To actually start mining, you'll need to use the wallet and generate a new address that should receive the mining rewards::

    ./wallet.py --wallet mining.wallet create-address mining-address.pem

Afterwards, you can copy the file `mining-address.pem` to the second machine and restart the miner like this::

    ./miner.py --bootstrap-peer a.b.c.d:1234 --mining-pubkey mining-address.pem

This miner will now mine new blocks for the block chain and send them to the miner application on
the other machine. Once some blocks have been mined, you can check how much money you have made like this::

    ./wallet.py --wallet mining.wallet show-balance

Once you have earned money mining, you can send some of it to someone else. To send them 42 coins (we already know how the other person can generate an address), you can do this::

    ./wallet.py --wallet mining.wallet transfer other_person_address.pem 42

Both the miner and the wallet have many more options than just these, which can be found using the `--help` switch of the programs. Especially useful might also be the `--rpc-port` option of the miner, which needs to be set to different values when one wants to start more than one instance on the same computer::

    ./miner.py --rpc-port 2345 --listen-port 1234
    ./miner.py --rpc-port 3456 --bootstrap-peer 127.0.0.1:1234
    ./wallet.py --miner-port 2345 --wallet mining.wallet show-balance





Source Code Documentation
*************************

.. autosummary::
    :toctree: _autosummary

    src.blockchain
    src.block
    src.chainbuilder
    src.crypto
    src.merkle
    src.mining
    src.mining_strategy
    src.proof_of_work
    src.protocol
    src.transaction
    src.persistence
    src.rpc_client
    src.rpc_server

Tests
*****
To run the tests, just run the `pytest` command.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
-->

# labVM Documentation 

## Basics
The labVM is a stack-based Virtual Machine. The Stack can hold references to either Integer or Strings of arbitrary size.

## Registers and Data Structures

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
| OP_ADD |- | consumes the two highest stack cells and pushes s_2 + s_1 |
| OP_SUB |- | consumes the two highest stack cells and pushes s_2 - s_1 |
| OP_MUL |- | consumes the two highest stack cells and pushes s_2 * s_1 |
| OP_DIV |- | consumes the two highest stack cells and pushes s_2 / s_1 |
| OP_MOD |- | consumes the two highest stack cells and pushes s_2 % s_1 |
| OP_AND |- | consumes the two highest stack cells and pushes s_2 & s_1 |
| OP_OR | -| consumes the two highest stack cells and pushes s_2 \| s_1 |
| OP_XOR |- | consumes the two highest stack cells and pushes s_2 ^ s_1 |
| OP_NEG |- | consumes the highest stack cell and pushes -s_1 |
| OP_NOT |- | consumes the highest stack cell and pushes 1 - s_1 |
| OP_SWAP | | Swaps s_1 and s_2|
| OP_DUP |- | pushes s_1 |
| OP_PUSHABS |- | pushes the the n-th cell of the stack. The lowest stack cell has index 0, the next one 1 and so on. |
| OP_PUSHFP |- | pushes the FramePointer |
| OP_PUSHSP |- | pushes the StackPointer |
| OP_POPFP |- | pops into the FramePointer |
| OP_POPSP |- | pops into the StackPointer |


