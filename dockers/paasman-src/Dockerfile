FROM paasman/base

MAINTAINER paasman

# download the project and place it under paasman
ADD https://github.com/ahlen/paasman/archive/master.tar.gz paasman-src/
RUN cd paasman-src && tar -xzvf master.tar.gz --strip-components 1

RUN cd paasman-src && pip install -r requirements.txt