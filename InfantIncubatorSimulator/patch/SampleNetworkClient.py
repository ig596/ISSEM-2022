import configparser
import hashlib
import math
import os
import socket
import time

import cryptography.fernet
import matplotlib.animation as animation
import matplotlib.pyplot as plt


class SimpleNetworkClient:
    def __init__(self, port1, port2, password, key):
        self.fig, self.ax = plt.subplots()
        now = time.time()
        self.lastTime = now
        self.times = [time.strftime("%H:%M:%S", time.localtime(now - i)) for i in range(30, 0, -1)]
        self.infTemps = [0] * 30
        self.incTemps = [0] * 30
        self.infLn, = plt.plot(range(30), self.infTemps, label="Infant Temperature")
        self.incLn, = plt.plot(range(30), self.incTemps, label="Incubator Temperature")
        plt.xticks(range(30), self.times, rotation=45)
        plt.ylim((20, 50))
        plt.legend(handles=[self.infLn, self.incLn])
        self.infPort = port1
        self.incPort = port2
        self.password = password
        self.crypto = cryptography.fernet.Fernet(key=key)
        self.infToken = None
        self.incToken = None

        self.ani = animation.FuncAnimation(self.fig, self.updateInfTemp, interval=500)
        self.ani2 = animation.FuncAnimation(self.fig, self.updateIncTemp, interval=500)

    def updateTime(self):
        now = time.time()
        if math.floor(now) > math.floor(self.lastTime):
            t = time.strftime("%H:%M:%S", time.localtime(now))
            self.times.append(t)
            # last 30 seconds of of data
            self.times = self.times[-30:]
            self.lastTime = now
            plt.xticks(range(30), self.times, rotation=45)
            plt.title(time.strftime("%A, %Y-%m-%d", time.localtime(now)))

    def getTemperatureFromPort(self, p, tok):
        # print("token:", tok)
        s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        s.sendto(self.crypto.encrypt(("%s;GET_TEMP" % tok).encode('utf-8')), ("127.0.0.1", p))
        msg, addr = s.recvfrom(1024)
        m = self.crypto.decrypt(msg).decode("utf-8")
        try:
            value, new_token_str = m.split(";")
            return float(value), new_token_str[6:]
        except:
            return 0, None

    def authenticate(self, p, pw):
        s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        msg = self.crypto.encrypt(b"AUTH %s" % pw)
        # print(msg)
        s.sendto(msg, ("127.0.0.1", p))
        msg, addr = s.recvfrom(1024)
        # print(msg)
        msg = self.crypto.decrypt(msg)
        # print(msg)
        return msg.decode("utf-8").strip()

    def updateInfTemp(self, frame):
        self.updateTime()
        if self.infToken is None:  # not yet authenticated
            self.infToken = self.authenticate(self.infPort,
                                              hashlib.sha256(self.password.encode("utf-8")).hexdigest().encode("utf-8"))

        temp, new_token = self.getTemperatureFromPort(self.infPort, self.infToken)
        self.infToken = new_token
        # print("new token:", self.infToken)
        self.infTemps.append(temp - 273)
        # self.infTemps.append(self.infTemps[-1] + 1)
        self.infTemps = self.infTemps[-30:]
        self.infLn.set_data(range(30), self.infTemps)
        return self.infLn,

    def updateIncTemp(self, frame):
        self.updateTime()
        if self.incToken is None:  # not yet authenticated
            self.incToken = self.authenticate(self.incPort,
                                              hashlib.sha256(self.password.encode("utf-8")).hexdigest().encode("utf-8"))

        temp, new_token = self.getTemperatureFromPort(self.incPort, self.incToken)
        self.incToken = new_token
        self.incTemps.append(temp - 273)
        # self.incTemps.append(self.incTemps[-1] + 1)
        self.incTemps = self.incTemps[-30:]
        self.incLn.set_data(range(30), self.incTemps)
        return self.incLn,


parser = configparser.ConfigParser(strict=False, interpolation=None)
parser.read(filenames=f'{os.path.dirname(__file__)}/../config.ini')
password = parser['configs']["PASSWORD"]
key = parser['configs']['key']
snc = SimpleNetworkClient(23459, 23457, password, key)

plt.grid()
plt.show()
