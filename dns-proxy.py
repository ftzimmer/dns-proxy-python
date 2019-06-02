#!/usr/bin/env python3

import sys
import socket
import selectors
import types
import struct
import ssl
#from dnslib import DNSRecord
#from dnslib.server import DNSServer,DNSHandler,BaseResolver,DNSLogger

sel = selectors.DefaultSelector()

host = "0.0.0.0"
port = 53
dns_tls_server = "1.1.1.1"
tlsport = 853

def tcp_dns_query(rcvd_query):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #defining the TLS security requirements for the connection
    context = ssl.SSLContext()
    context.verify_mode = ssl.CERT_REQUIRED
    context.check_hostname = True
    context.load_default_certs()
    # wraping the socket
    wrappedSocket = context.wrap_socket(sock, server_hostname='cloudflare-dns.com')
    # connect and print reply
    wrappedSocket.connect((dns_tls_server, tlsport))
    wrappedSocket.send(rcvd_query)
    query_response = wrappedSocket.recv(8192)
    # close socket
    wrappedSocket.close()
    sock.close()
    return query_response

## creates the indiviual connections and it's selector
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


#listens to the connection and the thread to read and write. 
def read_write_conn(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(8192)  # Should be ready to read
        if recv_data:
            data.recvd_q += recv_data
        else:
            print("closing connection to", data.addr)
            sel.unregister(sock)
            sock.close()
            
    if mask & selectors.EVENT_WRITE:
            if data.recvd_q:
                data.return_q = (tcp_dns_query(data.recvd_q))
                sent = sock.send(data.return_q)  # Should be ready to write
                data.return_q = data.return_q[sent:]
                data.recvd_q = data.return_q

#creates the tcp socket to listen and assigns to the selector
tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_sock.bind((host, port))
tcp_sock.listen()
tcp_sock.setblocking(False)
sel.register(tcp_sock, selectors.EVENT_READ, data=None)
#creating the udp socket to listen and also asign to selector
udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_sock.bind((host, port))
udp_sock.setblocking(False)
sel.register(udp_sock, selectors.EVENT_READ, data=None)

#loop to keep listening and alternating into selectors
try:
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_conn(key.fileobj)
            else:
                read_write_conn(key, mask)
               
#stops if pressing ctrl+D on keyboard
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
finally:
    sel.close()

