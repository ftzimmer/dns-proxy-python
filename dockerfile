FROM ubuntu:18.04
LABEL mantainer="ftzimmer@gmail.com"
RUN apt-get update && apt-get install -y \
	python3.7 \
	openssl \
	ca-certificates \
	wget \
RUN mkdir -p /src/
WORKDIR /src
RUN wget https://raw.githubusercontent.com/ftzimmer/dns-proxy-python/master/dns-proxy.py
EXPOSE 53
EXPOSE 53/udp
EXPOSE 853

ENTRYPOINT python3.7 dns-proxy.py