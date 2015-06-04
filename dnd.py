#!/usr/bin/env python

from socket import *

# connection info
TCP_IP = "129.170.208.9"
#TCP_IP = "129.170.194.174"
TCP_PORT = 902
BUFFER_SIZE = 4096

def loop():
    # create a socket and connect, printing initial response
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect((TCP_IP, TCP_PORT))
    data = sock.recv(BUFFER_SIZE)

    print "<<< " + data

    # main loop for query/response exchange
    message = ""
    while(message != "QUIT\r\n"):
        message += raw_input(">>> ")
        message += "\r\n" # have to append this for protocol to work
        sock.send(message)
        data = sock.recv(BUFFER_SIZE)
        # this is a little hack to make sure the last line
        # doesn't start with a 1 -- that would indicate it is not
        # the last response, so we keep receiving. simply
        # increasing the buffer size didn't seem to solve this
        while(data.splitlines()[-1].startswith("1")):
            data += s.recv(BUFFER_SIZE)

            print data
            message = ""

# given a name, returns an array of names
def fetch(name):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect((TCP_IP, TCP_PORT))
    data = sock.recv(BUFFER_SIZE)
    sock.send("lookup " + name + " 1, name deptclass\r\n")
    data = sock.recv(BUFFER_SIZE)
    while(data.splitlines()[-1].startswith("1")):
        data += line
    strings =  map(lambda s: s.split("110 ")[1], data.strip().split("\r\n")[1:-1])
    # return [ strings[i] + ' ' + strings[i+1] for i in range(0, len(strings)/2 + 1, 2) ]
    return [ strings[i] for i in range(0, len(strings)/2 + 1, 2) ]

