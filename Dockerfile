FROM ubuntu:18.04

RUN apt-get update && \
        apt-get install -y python3 python3-venv python3-pip git

RUN apt-get -y install make build-essential libssl-dev zlib1g-dev libbz2-dev \
        libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev \
        libncursesw5-dev xz-utils python3-openssl liblzma-dev
RUN env ln -fs /usr/share/zoneinfo/Etc/UTC /etc/localtime && \
    env DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata && \
    env DEBIAN_FRONTEND=noninteractive dpkg-reconfigure --frontend noninteractive tzdata        
RUN apt-get -y install proj-bin libgdal20 libgeos-dev \
       tk-dev libffi-dev       
RUN apt-get -y install libproj-dev automake autoconf

RUN python3 -m venv /login
RUN . /login/bin/activate && \
  pip install cython numpy
RUN . /login/bin/activate && \ 
  pip install ipython cartopy siphon metpy ipykernel pylzma
RUN . /login/bin/activate && \
    pip install pyinstrument==3.0.3
# When running this container, must run with "--cap-add SYS_PTRACE"
# for py-spy
RUN . /login/bin/activate && \
    pip install py-spy==0.1.11
RUN . /login/bin/activate && \
    cd /tmp; git clone https://github.com/P403n1x87/austin && \
    cd austin && git checkout v1.0.0 && \
    autoreconf || automake --add-missing  && autoreconf && \
    ./configure --prefix=/login && \
    make && make install
    
COPY generate_data.py /data/
COPY basic_stats.py /data/
