# labChain

This project is a completely new blockchain-based coin, with P2P networking, a consensus mechanism and a wallet interface. The goal of the project is to provide a framework that is easy to modify for people who want to develop proof-of-concepts for blockchain-based technology.

**DO NOT USE THIS AS A REAL CURRENCY TO SEND, RETRIEVE, OR STORE ACTUAL MONEY!** While we do not currently know of any way to do so, there are almost certainly bugs in this implementation that would allow anyone to create money out of the blue or take yours away from you.

Click the link below for the full documentation.

http://labchain.readthedocs.io/en/latest/

## Contents

<!-- TOC -->

- [labChain](#labchain)
    - [Contents](#contents)
    - [Running the Code](#running-the-code)
        - [Ubuntu / Debian GNU/Linux](#ubuntu--debian-gnulinux)
        - [Nix / NixOS](#nix--nixos)

<!-- /TOC -->

## Running the Code

You need `python3` to be able to run the code.
To install the requirements (that are listed in [requirements.txt](requirements.txt)) with pip, you should run the command `pip install -r requirements.txt`.

### Ubuntu / Debian GNU/Linux

If you are in a Debian variant OS you can run the following commands (from inside the labchain code folder) to have everything set-up:

```
sudo apt-get install python3
sudo apt-get install python3-pip
sudo python3 -m pip install -r requirements.txt
```

### Nix / NixOS

If you are on NixOS or have the Nix package manager installed, just execute `nix run` from inside the repository root folder.
