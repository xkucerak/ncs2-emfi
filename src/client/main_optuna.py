from logger import Config
import socket
import optuna
from tqdm import tqdm
from chipshouter import ChipSHOUTER
from ctl import Control
from time import sleep


SERVER_IP = "10.0.0.2"
PORT = 5050


def objective(trial: optuna.trial.BaseTrial):
    print("Request sent!")
    cs.pulse.repeat = 1  # trial.suggest_int("repeat", 1, 25)
    cs.pulse.deadtime = 1  # trial.suggest_int("deadtime", 1, 50)
    cs.voltage = trial.suggest_int("voltage", 150, 500)
    cs.pulse.width = 80 * trial.suggest_int("width", 1, 3)

    printer.move_3D(
        trial.suggest_float("x", 120, 124, step=0.1),
        trial.suggest_float("y", 153, 157, step=0.1),
        trial.suggest_float("z", 0.5, 2, step=0.1),
    )

    ATTEMPTS = 2**0

    score = 0
    fail_rate = 0

    for _ in range(ATTEMPTS):
        sleep(1)
        cs.pulse = True
        print("pulse")
        sleep(1)
        s.sendall(b"run")
        # sleep(1)

        # sleep(trial.suggest_float("delay", 0, 1, step=0.01))
        top_1, _ = s.recv(1024).decode().split(",")
        top_1 = float(top_1)

        if top_1 == -1:
            top_1 += 1
            score += float(cfg.cfg_top_1)
        else:
            score += top_1

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

    printer = Control(113, 127, 148, 160, 0.5, 2)

    if cs.armed == 0:
        cs.armed = 1

    study = optuna.create_study(
        storage="sqlite:///pre_infer.sqlite3",
        study_name="resnet_50_64img_1pls_1sample_pre_infer",
        sampler=optuna.samplers.TPESampler(multivariate=True, group=True),
        load_if_exists=True,
    )
    study.optimize(objective, n_trials=2000)
