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
Test using "dig" to your container IP, example below:
$ dig google.com.br @172.17.0.2

$ dig google.com.br @172.17.0.2 +tcp
