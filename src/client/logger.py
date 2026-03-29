import csv
from pathlib import Path
from dataclasses import dataclass, asdict
from jinja2 import Template, DictLoader


@dataclass
class Position:
    pos_x: float = None
    pos_y: float = None
    pos_z: float = None


@dataclass
class Cs:
    cs_voltage: int = None
    cs_repeat: int = None
    cs_width: int = None
    cs_deadtime: int = None


@dataclass
class Probe:
    probe_core: int = None
    probe_winding: str = None
    probe_rotation: str = None


@dataclass
class Config:
    cfg_delay: float = None
    cfg_model: str = None
    cfg_img_count: int = None
    cfg_img_seed: int = None
    cfg_top_1: float = None
    cfg_top_5: float = None


@dataclass
class Accuracy:
    top_1: float = None
    top_5: float = None


class Logger:
    def __init__(self, suffix: str):
        SAVE_PATH = (
            Path(__file__).resolve().parent.parent.parent / "results/exploratory"
        )

        self.num = 0
        for dir in SAVE_PATH.iterdir():
            temp = int(dir.name.split("_")[0])
            if temp > self.num:
                self.num = temp

        SAVE_PATH = SAVE_PATH / (str(self.num + 1).zfill(4) + "_" + suffix)
        SAVE_PATH.mkdir(parents=True, exist_ok=True)

        self.settings_file = SAVE_PATH / "settings.csv"
        self.results_file = SAVE_PATH / "results.csv"
        self.readme_file = SAVE_PATH / "README.md"

    def log(self, *args):

        data = {}

        allow_list = [Cs, Position, Accuracy]

        for cls in allow_list:
            for obj in args:
                if isinstance(obj, cls):
                    data |= asdict(obj)

        file_exists = self.results_file.exists()

        with open(self.results_file, "a", newline="") as f:
            writer = csv.DictWriter(f, data.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(data)

    def settings(self, cs: Cs, probe: Probe, position: Position, config: Config):

        settings_data = {}

        for obj in [cs, probe, position, config]:
            settings_data |= asdict(obj)

        with open(self.settings_file, "w", newline="") as f:
            writer = csv.DictWriter(f, settings_data.keys())
            writer.writeheader()
            writer.writerow(settings_data)

        template = Template(
            (Path(__file__).parent / "templates" / "point.md").read_text()
        )

        self.readme_file.write_text(template.render(**settings_data))
