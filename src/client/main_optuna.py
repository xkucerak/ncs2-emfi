from logger import Config
import socket
import optuna
from tqdm import tqdm
from chipshouter import ChipSHOUTER
from ctl import Control
from time import sleep
from optuna_integration import BoTorchSampler


SERVER_IP = "10.0.0.2"
PORT = 5050


def objective(trial: optuna.trial.BaseTrial):
    print("Request sent!")
    cs.pulse.repeat = 1  # trial.suggest_int("repeat", 1, 25)
    cs.pulse.deadtime = 1  # trial.suggest_int("deadtime", 1, 50)
    cs.voltage = 350  # trial.suggest_int("voltage", 150, 500, step=10)
    cs.pulse.width = 80 * 2  # trial.suggest_int("width", 1, 3)

    if cs.armed == 0:
        cs.armed = 1

    printer.move_3D(
        trial.suggest_float("x", 113, 127, step=0.5),
        trial.suggest_float("y", 148, 160, step=0.5),
        # 123.4,
        # 155.1,
        # trial.suggest_float("x", 120, 124, step=0.1),
        # trial.suggest_float("y", 153, 157, step=0.1),
        # trial.suggest_float("z", 0, 1, step=0.05),
        0.25,
    )

    ATTEMPTS = 2**1

    score = 0
    fail_rate = 0
    i = 0

    top_1_arr = []

    while i < ATTEMPTS:
        # sleep(0.5)
        # cs.pulse = True
        # print("PLS")
        # sleep(0.5)
        # s.sendall(b"run")
        # sleep(1)

        s.sendall(b"run")
        sleep(0.5)
        cs.pulse = True
        print("PLS")

        # sleep(trial.suggest_float("delay", 0, 1, step=0.01))
        top_1, _ = s.recv(1024).decode().split(",")
        top_1 = float(top_1)

        top_1_arr.append(top_1)

        if top_1 == -1:
            score += float(cfg.cfg_top_1) * 1.2
            fail_rate += 1
        else:
            score += top_1
            if top_1 != float(cfg.cfg_top_1):
                ATTEMPTS += 1
                if top_1 < (float(cfg.cfg_top_1) * 0.7):
                    ATTEMPTS += 2
        i += 1

    trial.set_user_attr("failed", fail_rate)
    trial.set_user_attr("attempts", ATTEMPTS)
    trial.set_user_attr("top-1", top_1_arr)
    print("Result:", score / ATTEMPTS)
    return score / ATTEMPTS  # , (fail_rate / ATTEMPTS)


cfg = Config()

if __name__ == "__main__":

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((SERVER_IP, PORT))

    s.sendall(b"run")
    cfg.cfg_top_1, cfg.cfg_top_5 = s.recv(1024).decode().split(",")

    cs = ChipSHOUTER("/dev/ttyUSB1")

    cs.pulse.repeat = 1
    cs.pulse.deadtime = 25
    cs.voltage = 350
    cs.pulse.width = 80 * 2

    printer = Control("/dev/ttyUSB0", 113, 127, 148, 160, 0, 2)

    if cs.armed == 0:
        cs.armed = 1

    study = optuna.create_study(
        storage="sqlite:///pulse_before_infer.sqlite3",
        study_name="resnet_50_128img_2d_scan",
        sampler=optuna.samplers.TPESampler(multivariate=True, group=True),
        # sampler=optuna.samplers.CmaEsSampler(),
        # sampler=optuna.samplers.QMCSampler(scramble=True),
        load_if_exists=True,
    )
    study.optimize(objective, n_trials=5_000)
