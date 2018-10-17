FROM ubuntu:17.10

WORKDIR /IasisLCExplorationService
ADD . /IasisLCExplorationService

RUN apt-get --assume-yes update
RUN apt-get --assume-yes upgrade
RUN apt-get --assume-yes install python3 python3-numpy python3-flask python3-sparqlwrapper gunicorn3

# Make port 5003 available to the world outside this container
EXPOSE 5003

# Define environment variable
ENV NAME IasisLCExploration

# Run app.py when the container launches
CMD ./run_iasis_lc_exploration_service.sh

