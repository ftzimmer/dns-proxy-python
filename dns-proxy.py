#!/usr/bin/env python3

import sys
import socket
import selectors
import types
import struct
import ssl


## Variables to define the adress to listen and to connect to Cloudfare server
host = "0.0.0.0"
port = 53
dns_tls_server = "1.1.1.1"
tlsport = 853
sel = selectors.DefaultSelector()

## Function that performs the dns over tls queries.
## It receives the original query as a parameter when called and return the response from CloudFare
def tcp_dns_query(rcvd_query):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #defining the TLS security requirements for the connection
    context = ssl.SSLContext()
    context.verify_mode = ssl.CERT_REQUIRED
    context.check_hostname = True
    context.load_default_certs()
    # wraping the socket
    wrappedSocket = context.wrap_socket(sock, server_hostname='cloudflare-dns.com')
    # connect to cloudfare send the query and get the response
    wrappedSocket.connect((dns_tls_server, tlsport))
    wrappedSocket.send(rcvd_query)
    query_response = wrappedSocket.recv(8192)
    wrappedSocket.close()
    sock.close()
    return query_response

## Creates the indiviual socket connections and it's selector
## It has a condition to know if TCP or UDP. 
## In case TCP request it uses the selector that alternates between Read and Write
## In case UPD, immediately calls the function to make the request to Cloudfare 
def accept_conn(sock):
    if sock.type == True:
        conn, addr = sock.accept()
        conn.setblocking(False)
        data = types.SimpleNamespace(addr=addr, return_q=b"", recvd_q=b"")
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        sel.register(conn, events, data=data)
    elif sock.type.SOCK_DGRAM:
        data, address = sock.recvfrom(4096)
        if data:
            #transform UDP DNS in TCP DNS format
            query = struct.pack("!H",len(data)) + data
            #call the function that resolves the DNS
            response = tcp_dns_query(query)
            #transforms back to UDP format
            response = response[2:]
            sock.sendto(response, address)


#When called via the main loop it alternates between read and write to be able manage multiple connections. 
def read_write_conn(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(8192)
        if recv_data:
            data.recvd_q += recv_data
        else:
            sel.unregister(sock)
            sock.close()           
    if mask & selectors.EVENT_WRITE:
            if data.recvd_q:
                data.return_q = (tcp_dns_query(data.recvd_q))
                sent = sock.send(data.return_q)
                data.return_q = data.return_q[sent:]
                data.recvd_q = data.return_q

#Creates the tcp socket to listen and assign to selector
tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_sock.bind((host, port))
tcp_sock.listen()
tcp_sock.setblocking(False)
sel.register(tcp_sock, selectors.EVENT_READ, data=None)
#Creates the udp socket to listen and also assign to selector
udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_sock.bind((host, port))
udp_sock.setblocking(False)
sel.register(udp_sock, selectors.EVENT_READ, data=None)

#Loop to keep listening and alternating into selectors
try:
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_conn(key.fileobj)
            else:
                read_write_conn(key, mask)
               
#keyboard interruption
except KeyboardInterrupt:
    print("interruption caught, exiting")
finally:
    sel.close()

