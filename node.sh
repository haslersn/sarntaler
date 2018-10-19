#!/usr/bin/env sh
export FLASK_APP=src/node/flask_node.py
export FLASK_ENV=development
export FLASK_DEBUG=1
python3 -m flask run
