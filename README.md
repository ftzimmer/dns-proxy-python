# dns-proxy-python
DNS Proxy using Python that handles UDP and TCP requests and forward them to Cloudfare DNS servers using DNS over TLS

How to build image:
```
docker image build -t challenge:dns-proxy .
```
Run using:
```
docker container run -d challenge:dns-proxy
```
You can optionally run the image directly from docker hub:
```
docker container run -d ftzimmer/challenge:dns-proxy
```
Test using "dig" to your container IP, examples below:
```
dig google.com.br @172.17.0.2
```
```
dig google.com.br @172.17.0.2 +tcp
```
