FROM paasman/paasman-src

MAINTAINER paasman

#RUN echo "deb http://archive.ubuntu.com/ubuntu precise main universe" > /etc/apt/sources.list
#RUN apt-get update

#RUN DEBIAN_FRONTEND=noninteractive apt-get install -q -y curl wget
#RUN DEBIAN_FRONTEND=noninteractive apt-get install -q -y python
#RUN DEBIAN_FRONTEND=noninteractive apt-get install -q -y python-pip
#RUN DEBIAN_FRONTEND=noninteractive apt-get install -q -y python-dev

# build things
#RUN DEBIAN_FRONTEND=noninteractive apt-get install -q -y libtool autoconf automake uuid-dev build-essential g++ make

# libevent, used by gevent
#RUN DEBIAN_FRONTEND=noninteractive apt-get install -q -y libevent-dev

#RUN wget http://download.zeromq.org/zeromq-2.2.0.tar.gz
#RUN tar xzvf zeromq-2.2.0.tar.gz
#RUN cd zeromq-2.2.0 && ./configure
#RUN cd zeromq-2.2.0 && make && make install

# download the project and place it under paasman
#ADD https://github.com/ahlen/paasman/archive/master.tar.gz paasman-src/
#RUN cd paasman-src && tar -xzvf master.tar.gz --strip-components 1

#RUN cd paasman-src && pip install -r requirements.txt

# 5555 for the publishing zeromq socket
# 5111 for the server(rep) zeromq socket
# 8001 for the directors RESTful API
EXPOSE 5555 5111 8001

#ENTRYPOINT ["python", "paasman-src/wsgi-director.py"]

CMD ["/bin/bash"]