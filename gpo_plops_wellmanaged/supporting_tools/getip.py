#!/bin/env python3
## importing socket module
import socket
import sys
## getting the hostname by socket.gethostname() method
hostname = socket.gethostname()
## getting the IP address using socket.gethostbyname() method
try:
  ip_address = socket.gethostbyname(sys.argv[1])
except:
  ip_address="UNKNOWN"
print(ip_address)
