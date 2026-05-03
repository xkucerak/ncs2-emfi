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
cs.voltage = 348  # 425
cs.pulse.width = 80 * 2

cs.pat_wave = [0, 1, 1, 1, 1, 1, 0]
cs.pat_enable = 0

print("cs init done")

printer = Control("/dev/ttyUSB0", 113, 127, 148, 160, 0, 2)
# printer.move_3D(116.3, 154.9, 0.25)
# printer.move_3D(116.3, 154.8, 0.53)
# printer.move_3D(123.4, 155.1, 0.25)
# printer.move_3D(123, 155, 0.25)


print("3d init done")

delay = -0.5  # 3.222

cfg = Config(cfg_delay=delay)

s.sendall(b"info")
cfg.cfg_model, cfg.cfg_img_count, cfg.cfg_img_seed = s.recv(1024).decode().split(",")

print("calib run start")
s.sendall(b"run")
cfg.cfg_top_1, cfg.cfg_top_5 = s.recv(1024).decode().split(",")
print("calib run finish")

log = Logger("1mm_ccw")

cs_log = Cs()

if cs.pat_enable:
    cs_log.cs_width = cs.pat_wave.count("1") * 20
else:
    cs_log.cs_width = cs.pulse.width

cs_log.cs_voltage = cs.voltage.set
cs_log.cs_repeat = cs.pulse.repeat
cs_log.cs_deadtime = cs.pulse.deadtime


log.settings(
    cs_log,
    Probe(1, "ccw", "right"),
    Position(*printer.get_pos()),
    cfg,
)

if cs.armed == False:
    cs.armed = True
    sleep(1)

acc = Accuracy()

for _ in tqdm(range(2**9)):
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
    sleep(0.5)  # 0.5

cs.armed = False
cs.disconnect()
