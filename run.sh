#!/bin/bash

if [ -f /app/requirements.txt ]; then
    echo 'Installing requirements '
    pip3 install -r requirements.txt
    echo 'starting flask app.'
    flask run --host 0.0.0.0 --port 5000
else
    echo 'starting flask app.'
    flask run --host 0.0.0.0 --port 5000
fi