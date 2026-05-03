from logger import *
import socket
from chipshouter import ChipSHOUTER
from time import sleep
from ctl import Control
from tqdm import tqdm

SERVER_IP = "10.0.0.2"
PORT = 5050

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((SERVER_IP, PORT))

cs = ChipSHOUTER("/dev/ttyUSB1")

cs.pulse.repeat = 1
cs.pulse.deadtime = 1
cs.voltage = 425
cs.pulse.width = 80 * 2

cs.pat_wave = [0, 1, 1, 1, 1, 1, 0]
cs.pat_enable = 1

print("cs init done")

printer = Control("/dev/ttyUSB0", 113, 127, 148, 160, 0, 2)
printer.move_3D(116.3, 154.8, 0.53)


delay = 2

cfg = Config()

print("No Injection Accuraccy Test")
s.sendall(b"run")
cfg.cfg_top_1, cfg.cfg_top_5 = s.recv(1024).decode().split(",")
print(cfg.cfg_top_1, cfg.cfg_top_5)


if cs.armed == False:
    cs.armed = True
    sleep(1)

acc = Accuracy()

for _ in tqdm(range(2**8)):
    if delay < 0:
        sleep(abs(delay))
        cs.pulse = True
        sleep(abs(delay))
        s.sendall(b"run")
    else:
        s.sendall(b"run")
        sleep(delay)
        cs.pulse = True
    acc.top_1, acc.top_5 = s.recv(1024).decode().split(",")
    if float(acc.top_1) < float(cfg.cfg_top_1) * 0.9 and acc.top_1 != "-1":
        break
    sleep(0.5)

cs.armed = False
cs.disconnect()
