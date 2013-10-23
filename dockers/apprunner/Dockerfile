FROM paasman/nodebase

MAINTAINER paasman

#ADD container.js /paasman-node/container.js
ADD runner.sh /paasman-node/runner.sh

RUN chmod +x /paasman-node/runner.sh
#CMD ["chmod +x", "/paasman-node/runner.sh"]

#CMD ["./paasman-node/runner.sh"]

# TODO: fetch the file from 

# we expose port 80 but this will be mapped to a random port on the outside
EXPOSE 80

#ADD run /runner

CMD ["./paasman-node/runner.sh"]

#CMD ["/bin/bash"]

#CMD ["nodejs", "/app/container.js", "/app/deployed/"]
