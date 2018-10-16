#!/bin/bash

echo "***** Running the service on port 5003 ***** "
gunicorn3 -w 4 -b 0.0.0.0:5003 --timeout 9000 iasis_KG_exploration_service:app
