FROM paasman/base

ADD ./ /paasman-src

#RUN cd paasman-src && pip install -r requirements.txt

# expose everything
EXPOSE 80 8001 5555 5222 5111