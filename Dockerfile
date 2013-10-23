FROM paasman/base

ADD ./ /paasman-src

#RUN cd paasman-src && pip install -r requirements.txt

RUN mkdir /_deployments/

# expose everything
EXPOSE 80 8001 5555 5222 5111

WORKDIR /paasman-src