FROM debian

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y python python-pip git

RUN git clone https://github.com/hashbang/paest-server.git && \
    cd paest-server && \
    pip install -r requirements.txt

WORKDIR paest-server

EXPOSE 80

CMD ["./run.sh", "--redis_host=redis"]
