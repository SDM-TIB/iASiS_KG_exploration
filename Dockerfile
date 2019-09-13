FROM ubuntu:18.04

WORKDIR /IasisLCExplorationService
ADD . /IasisLCExplorationService

RUN apt-get --assume-yes update
RUN apt-get --assume-yes upgrade
RUN apt-get --assume-yes install python3 python3-flask python3-sparqlwrapper

# Make port 5003 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV NAME IasisLCExploration

# Run app.py when the container launches
CMD ./run_iasis_lc_exploration_service.sh

