from logger import *
import socket
from chipshouter import ChipSHOUTER
from time import sleep
from ctl import Control


SERVER_IP = "10.0.0.2"
PORT = 5050

printer = Control(113, 127, 148, 160, 1, 2)

cs = ChipSHOUTER("/dev/ttyUSB1")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((SERVER_IP, PORT))

cs.pulse.repeat = 17
cs.pulse.deadtime = 25
cs.voltage = 440
cs.pulse.width = 80 * 2

printer.move_3D(122.4, 155.2, 1.1)
delay = 1

cfg = Config(cfg_delay=delay)

s.sendall(b"info")
cfg.cfg_model, cfg.cfg_img_count = s.recv(1024).decode().split(",")

s.sendall(b"run")
cfg.cfg_top_1, cfg.cfg_top_5 = s.recv(1024).decode().split(",")

log = Logger("spot")


log.settings(
    Cs(cs.voltage.set, cs.pulse.repeat, cs.pulse.width, cs.pulse.deadtime),
    Probe(1, "ccw", "right"),
    Position(*printer.get_pos()),
    cfg,
)

if cs.armed == False:
    cs.armed = True
    sleep(1)

acc = Accuracy()

for _ in range(128):
    s.sendall(b"run")
    cs.pulse = True
    print("pulse")
    acc.top_1, acc.top_5 = s.recv(1024).decode().split(",")
    log.log(acc)

cs.armed = False

cs.disconnect()
