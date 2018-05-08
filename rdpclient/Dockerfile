FROM ubuntu:xenial

RUN apt-get update
RUN apt-get install -y git cmake autoconf build-essential sudo

RUN mkdir /app/
WORKDIR /app/
RUN git clone https://github.com/FreeRDP/FreeRDP-WebConnect.git

WORKDIR /app/FreeRDP-WebConnect
RUN apt-get install -y iso-codes libpython-stdlib libpython2.7-minimal libpython2.7-stdlib python python-apt python-apt-common python-minimal python-pycurl python-software-properties python2.7 python2.7-minimal python3-apt unattended-upgrades
# RUN apt-get install apt-get install -y build-essential g++-4.8 libxml++2.6-dev libssl-dev libboost-all-dev libpng-dev libdwarf-dev subversion subversion-tools autotools-dev autoconf libtool cmake
# RUN apt-get install -y exim4 exim4-base exim4-config exim4-daemon-light heirloom-mailx icu-devtools libapr1 libaprutil1 libboost-all-dev libboost-atomic-dev libboost-atomic1.54-dev libboost-atomic1.54.0 libboost-chrono-dev libboost-chrono1.54-dev libboost-chrono1.54.0 libboost-context-dev libboost-context1.54-dev libboost-context1.54.0 libboost-coroutine-dev libboost-coroutine1.54-dev libboost-date-time-dev libboost-date-time1.54-dev libboost-date-time1.54.0 libboost-dev libboost-exception-dev libboost-exception1.54-dev libboost-filesystem-dev libboost-filesystem1.54-dev libboost-filesystem1.54.0 libboost-graph-dev libboost-graph-parallel-dev libboost-graph-parallel1.54-dev libboost-graph-parallel1.54.0 libboost-graph1.54-dev libboost-graph1.54.0 libboost-iostreams-dev libboost-iostreams1.54-dev libboost-iostreams1.54.0 libboost-locale-dev libboost-locale1.54-dev libboost-locale1.54.0 libboost-log-dev libboost-log1.54-dev libboost-log1.54.0 libboost-math-dev libboost-math1.54-dev libboost-math1.54.0 libboost-mpi-dev libboost-mpi-python-dev libboost-mpi-python1.54-dev libboost-mpi-python1.54.0 libboost-mpi1.54-dev libboost-mpi1.54.0 libboost-program-options-dev libboost-program-options1.54-dev libboost-program-options1.54.0 libboost-python-dev libboost-python1.54-dev libboost-python1.54.0 libboost-random-dev libboost-random1.54-dev libboost-random1.54.0 libboost-regex-dev libboost-regex1.54-dev libboost-regex1.54.0 libboost-serialization-dev libboost-serialization1.54-dev libboost-serialization1.54.0 libboost-signals-dev libboost-signals1.54-dev libboost-signals1.54.0 libboost-system-dev libboost-system1.54-dev libboost-system1.54.0 libboost-test-dev libboost-test1.54-dev libboost-test1.54.0 libboost-thread-dev libboost-thread1.54-dev libboost-thread1.54.0 libboost-timer-dev libboost-timer1.54-dev libboost-timer1.54.0 libboost-tools-dev libboost-wave-dev libboost-wave1.54-dev libboost-wave1.54.0 libboost1.54-dev libboost1.54-tools-dev libconfig-inifiles-perl libcr0 libdwarf-dev libelfg0 libexpat1-dev libglib2.0-0 libglib2.0-bin libglib2.0-data libglib2.0-dev libglibmm-2.4-1c2a libglibmm-2.4-dev libhwloc-dev libhwloc-plugins libhwloc5 libibverbs-dev libibverbs1 libicu-dev libicu52 liblist-moreutils-perl libltdl-dev libltdl7 libnuma1 libopenmpi-dev libopenmpi1.6 libpci-dev libpci3 libpciaccess0 libpcre3-dev libpcrecpp0 libpng12-dev libpython-dev libpython2.7 libpython2.7-dev libserf-1-1 libsigc++-2.0-0c2a libsigc++-2.0-dev libssl-dev libssl-doc libsvn-perl libsvn1 libtool libtorque2 liburi-perl libxml++2.6-2 libxml++2.6-dev libxml2-dev mpi-default-bin mpi-default-dev ocl-icd-libopencl1 openmpi-bin openmpi-common pkg-config psmisc python-subversion shared-mime-info subversion subversion-tools zlib1g-dev
RUN apt-get install -y zlib1g-dev libssl-dev libboost-all-dev libboost-atomic-dev libpng-dev libcpprest-dev
# RUN apt-get install -y freerdp
# RUN apt-get install -y software-properties-common 
# RUN apt-get install -y pkg-config
ADD setup.sh ./setup.sh
RUN echo asd
RUN ./setup.sh -f

WORKDIR /app/FreeRDP-WebConnect/wsgate/build
ADD wsgate.ini ./wsgate.ini
ADD webconnect.html ../webroot/index-debug.html
ADD clipboard.js ../webroot/js/clipboard.js
ADD run.sh ./run.sh

CMD ["./run.sh"]
