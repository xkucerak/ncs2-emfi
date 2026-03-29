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
cs.voltage = 348
cs.pulse.width = 80 * 2

print("cs init done")

printer = Control("/dev/ttyUSB0", 113, 127, 148, 160, 0.5, 2)
printer.move_3D(123.4, 155.1, 0.7)

print("3d init done")

delay = -1

cfg = Config(cfg_delay=delay)

s.sendall(b"info")
cfg.cfg_model, cfg.cfg_img_count, cfg.cfg_img_seed = s.recv(1024).decode().split(",")

print("calib run start")
s.sendall(b"run")
cfg.cfg_top_1, cfg.cfg_top_5 = s.recv(1024).decode().split(",")
print("calib run finish")

log = Logger("spot_1_pulse_pre_inf")

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
    log.log(acc)
    sleep(0.5)

cs.armed = False
cs.disconnect()
