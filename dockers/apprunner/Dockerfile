FROM paasman/nodebase

MAINTAINER paasman

ADD container.js /paasman-node/container.js

# TODO: fetch the file from 

# we expose port 80 but this will be mapped to a random port on the outside
EXPOSE 80

ADD run /usr/local/bin/run

CMD ["/usr/local/bin/run"]

#CMD ["nodejs", "/app/container.js", "/app/deployed/"]
