FROM ubuntu:18.04
LABEL mantainer="ftzimmer@gmail.com"
RUN apt-get update
RUN apt-get install -y python3.7
RUN apt-get install openssl
RUN apt-get install ca-certificates
RUN apt-get install -y wget
RUN mkdir -p /src/
WORKDIR /src
RUN git clone https://github.com/ftzimmer/dns-proxy-python
WORKDIR /dns-proxy-python
EXPOSE 53
EXPOSE 53/udp
EXPOSE 853

ENTRYPOINT python3.7 dns-proxy.py