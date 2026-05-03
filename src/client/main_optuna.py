from logger import Config
import socket
import optuna
import optunahub
from tqdm import tqdm
from chipshouter import ChipSHOUTER
from ctl import Control
from time import sleep
from optuna_integration import BoTorchSampler

SERVER_IP = "10.0.0.2"
PORT = 5050


def objective(trial: optuna.trial.BaseTrial):
    print("Request sent!")
    cs.pulse.repeat = 1  # trial.suggest_int("repeat", 1, 10)
    cs.pulse.deadtime = 1  # trial.suggest_int("deadtime", 1, 25)
    cs.voltage = 348  # trial.suggest_int("voltage", 150, 400, step=1)  # 350
    cs.pulse.width = 80 * 2  # trial.suggest_int("width", 1, 2)

    # cs.pat_wave = [0, *[1] * trial.suggest_int("width", 3, 8, step=1), 0]
    cs.pat_enable = 0

    if cs.armed == 0:
        cs.armed = 1

    area = 1

    printer.move_3D(
        # trial.suggest_float("x", 115, 125, step=0.1),
        # trial.suggest_float("y", 150, 158, step=0.1),
        # 122.1,
        # 155.0,
        # 123.4,
        # 155.1,
        # trial.suggest_float("x", 120, 125, step=0.0125),
        # trial.suggest_float("y", 152, 157, step=0.0125),
        trial.suggest_float("x", 123.5, 124.5, step=0.0125),
        trial.suggest_float("y", 154.5, 155.5, step=0.0125),
        # 123.6,
        # 155.0,
        # trial.suggest_float("z", 0, 1, step=0.01),
        0.25,
        # 0,
    )

    ATTEMPTS = 2**0

    score = 0
    fail_rate = 0
    i = 0

    top_1_arr = []

    while i < ATTEMPTS:
        if True:
            sleep(0.5)
            cs.pulse = True
            print("PLS")
            sleep(0.5)
            s.sendall(b"run")
        else:
            s.sendall(b"run")
            sleep(trial.suggest_float("delay", 0.5, 4, step=0.001))
            cs.pulse = True
            print("PLS")

        # sleep(trial.suggest_float("delay", 0, 1, step=0.01))
        top_1, _ = s.recv(1024).decode().split(",")
        top_1 = float(top_1)

        top_1_arr.append(top_1)

        if top_1 == -1:
            score += float(cfg.cfg_top_1)  # TODO
            fail_rate += 1
        else:
            score += top_1
            if top_1 != float(cfg.cfg_top_1):
                ATTEMPTS += 1
                if top_1 < (float(cfg.cfg_top_1) * 0.7):
                    ATTEMPTS += 2

        if i >= 3:
            if fail_rate == i + 1:
                ATTEMPTS = i + 1
                break

        i += 1

    trial.set_user_attr("failed", fail_rate)
    trial.set_user_attr("attempts", ATTEMPTS)
    trial.set_user_attr("top-1", top_1_arr)

    printer.move_3D(123, 154, 0.25)

    print("Result:", score / ATTEMPTS)
    return (score / ATTEMPTS,)  # (fail_rate / ATTEMPTS)


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
    cs.pat_enable = 0

    print(cs)

    printer = Control("/dev/ttyUSB0", 113, 127, 148, 160, 0, 2)

    if cs.armed == 0:
        cs.armed = 1

    study = optuna.create_study(
        storage="sqlite:///1mmccw_2.sqlite3",
        study_name="resnet50_pre_infer_neviem_detail_detail_move_repeat_fine",
        # sampler=optuna.samplers.TPESampler(),
        sampler=optuna.samplers.TPESampler(multivariate=True, group=True),
        # sampler=optuna.samplers.QMCSampler(scramble=True),
        # directions=["minimize", "minimize"],
        load_if_exists=True,
    )
    study.optimize(objective, n_trials=5_000)
