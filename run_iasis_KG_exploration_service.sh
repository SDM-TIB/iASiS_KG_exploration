#!/bin/bash

echo "***** Running the service on port 5002 ***** "
gunicorn3 -w 4 -b 0.0.0.0:5002 --timeout 9000 iasis_KG_exploration_service:app
