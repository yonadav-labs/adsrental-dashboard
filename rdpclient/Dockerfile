FROM ubuntu:16.04

RUN apt-get update
RUN apt-get install -y git cmake autoconf build-essential sudo

RUN mkdir /app/
WORKDIR /app/
RUN git clone https://github.com/FreeRDP/FreeRDP-WebConnect.git

WORKDIR /app/FreeRDP-WebConnect
RUN apt-get install -y apt-utils
RUN apt-get install -y iso-codes libpython-stdlib libpython2.7-minimal libpython2.7-stdlib python python-apt python-apt-common python-software-properties python-minimal python-pycurl python2.7 python2.7-minimal python3-apt unattended-upgrades
RUN apt-get install -y zlib1g-dev libssl-dev libboost-all-dev libboost-atomic-dev libpng-dev libcpprest-dev
RUN apt-get install -y libgstreamer0.10-dev libgstreamer-plugins-base0.10-dev libavcodec-dev libalsa-ocaml-dev libalsaplayer-dev

ADD setup.sh ./setup.sh
RUN ./setup.sh -f

WORKDIR /app/FreeRDP-WebConnect/wsgate/build
ADD wsgate.ini ./wsgate.ini
ADD webconnect.html ../webroot/index-debug.html
ADD clipboard.js ../webroot/js/clipboard.js
ADD run.sh ./run.sh

CMD ["./run.sh"]
