import configparser
import os
import socket
import time

import cryptography.fernet

mitmSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
mitmSocket.bind(("127.0.0.1", 23459))

s_rl = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

parser = configparser.ConfigParser(strict=False, interpolation=None)
parser.read(filenames=f'{os.path.dirname(__file__)}/../config.ini')
key = parser['configs']['key']
crypto = cryptography.fernet.Fernet(key=key)

while 1:
    input_request, client_addr = mitmSocket.recvfrom(1024)
    s_rl.sendto(input_request, ("127.0.0.1", 23456))
    output_responce, real_server_addr = s_rl.recvfrom(1024)
    mitmSocket.sendto(output_responce, client_addr)

    # Try to perform reply attack
    inp_req = crypto.decrypt(input_request).decode("utf-8")
    if not inp_req.startswith("AUTH"):
        s_rl.sendto(input_request, ("127.0.0.1", 23456))
        output_responce, _ = s_rl.recvfrom(1024)
        m = crypto.decrypt(output_responce).decode("utf-8")
        if m == "Bad Token\n":
            print(f"Reply attack failed, got Bad Token")
        else:
            print(f"Reply attack successful, got {m}")
