import cProfile
import logging as log
import re
import sys
import gc

# import cv2
from time import sleep, time
import subprocess
import multiprocessing as mp

import numpy as np
import torch
import torchmetrics
import socket

# from openvino.inference_engine import IECore
from openvino.preprocess import PrePostProcessor, ResizeAlgorithm
from openvino.runtime import Core, Layout, Type
from torch.utils.data import DataLoader
from torchvision import datasets
from torchvision.io import decode_image
from torchvision.models import ResNet50_Weights, resnet50
from tqdm import tqdm

device_name = "MYRIAD"

SIZE = 2**8

MODEL_PATH = "/home/pincs/Desktop/src/models/resnet101.onnx"
MODEL_PATH = "/home/pincs/Desktop/src/models/resnet50.onnx"
MODEL_PATH = "/home/pincs/Desktop/src/models/resnet18.onnx"
MODEL_PATH = "/home/pincs/Desktop/src/models/vgg11.onnx"


def create_val_loader():
    weights = ResNet50_Weights.DEFAULT
    dataset = datasets.ImageFolder(
        root="/home/pincs/Desktop/archive", transform=weights.transforms()
    )

    BATCH = 1

    subset, _ = torch.utils.data.random_split(
        dataset,
        [SIZE, len(dataset) - SIZE],
        generator=torch.Generator().manual_seed(21),
    )

    # for idx in subset.indices:
    #     path, label = dataset.samples[idx]
    #     print(path)
    # exit()

    val_loader = DataLoader(
        dataset=subset,
        batch_size=BATCH,
        # shuffle=True,
        num_workers=2,
        prefetch_factor=16,
        # pin_memory=True,
        persistent_workers=True,
    )

    return val_loader


preprocess = ResNet50_Weights.DEFAULT.transforms()


def model_prepare():

    image_path = "/home/pincs/Desktop/archive/00001/118374130323352.jpg"

    core = Core()

    print(core.available_devices)

    core.set_property({"CACHE_DIR": "/home/pincs/Desktop/src/cache"})
    # core.set_property("MYRIAD", {"MYRIAD_ENABLE_FORCE_RESET": "YES"})

    model = core.read_model(MODEL_PATH)

    if len(model.inputs) != 1:
        log.error("Sample supports only single input topologies")
        return -1

    if len(model.outputs) != 1:
        log.error("Sample supports only single output topologies")
        return -1

    image = decode_image(image_path)
    input_tensor = preprocess(image)

    input_tensor = np.expand_dims(input_tensor, 0)

    ppp = PrePostProcessor(model)

    ppp.input().tensor().set_shape(input_tensor.shape).set_element_type(
        Type.f32
    ).set_layout(
        Layout("NCHW")
    )  # noqa: ECE001, N400

    ppp.input().preprocess().resize(ResizeAlgorithm.RESIZE_LINEAR)
    ppp.input().model().set_layout(Layout("NCHW"))
    ppp.output().tensor().set_element_type(Type.f32)
    model = ppp.build()

    return model, core, input_tensor


def one_img(model, input_tensor, compiled_model):
    first = None
    raw = None
    score = 0

    try:
        for _ in range(32):
            last_resp.value = time()
            outputs = compiled_model.infer_new_request({0: input_tensor})
            output = list(outputs.values())[0]  # get the only output
            class_id = output.argmax(1).item()

            category_name = ResNet50_Weights.DEFAULT.meta["categories"][class_id]
            if first == None:
                raw = outputs
                first = category_name
                print("*" * 5, category_name, "*" * 5)

            if category_name != first:
                score += 0.5
                print(category_name)

            change = np.array_equal(list(outputs.values())[0], list(raw.values())[0])

            if change == False:
                score += 0.5

            print(".", change, _)

    except Exception as e:
        print(e)
        last_resp.value = time() + 60
        return -1 + (score / 32)

    last_resp.value = 0

    if device_name == "MYRIAD":
        temp = core.get_property("MYRIAD", "DEVICE_THERMAL")
        print(f"Device Temperature: {temp}°C")
    # compiled_model.create_infer_request()
    return score / 32


def full_eval(val_loader):
    # core = Core()
    # compiled_model = core.compile_model(model, device_name)
    try:
        top_1 = torchmetrics.Accuracy(top_k=1, task="multiclass", num_classes=1000)
        top_5 = torchmetrics.Accuracy(top_k=5, task="multiclass", num_classes=1000)
        for inputs, labels in tqdm(val_loader):
            last_resp.value = time()

            outputs = compiled_model.infer_new_request({0: inputs})

            outputs = torch.tensor(next(iter(outputs.values())))

            top_1.update(outputs, labels)
            top_5.update(outputs, labels)

        print(top_1.compute().item(), "%", top_5.compute().item(), "%")

        if device_name == "MYRIAD":
            temp = core.get_property("MYRIAD", "DEVICE_THERMAL")
            print(f"Device Temperature: {temp}°C")

    except Exception as e:
        print(e)
        last_resp.value = time() + 30
        return -1, -1

    last_resp.value = 0

    return top_1.compute().item(), top_5.compute().item()


def dog():
    while True:
        if last_resp.value != 0 and ((time() - last_resp.value) > 5):
            print("*" * 10)
            subprocess.run(["sudo", "uhubctl", "-l", "2", "-a", "2"])
            print("*" * 10)
            last_resp.value = time() + 60
        sleep(0.05)


if __name__ == "__main__":
    last_resp = mp.Value("d", 0)
    p = mp.Process(target=dog, daemon=True)
    p.start()

    model, core, input_tensor = model_prepare()

    compiled_model = core.compile_model(model, device_name)

    save = compiled_model.export_model()
    print("prep done")

    val_loader = create_val_loader()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", 5050))

    s.listen(1)

    top_1 = 0
    print("READY")
    conn, addr = s.accept()
    while True:
        print("wait")
        last_resp.value = 0

        data = conn.recv(1024).decode()
        if data == "run":
            print(data)

            # score = one_img(model, input_tensor, compiled_model)
            top_1, top_5 = full_eval(val_loader)
            if top_1 < 0:
                del compiled_model
                del core
                gc.collect()
                while True:
                    try:
                        start = time()
                        core = Core()
                        print(time() - start)
                        compiled_model = core.import_model(save, device_name)
                        print(time() - start)
                        break
                    except Exception as e:
                        print(e, 1)
                        sleep(0.5)
            while True:
                try:
                    try:
                        del compiled_model
                    except:
                        pass
                    compiled_model = core.import_model(save, device_name)
                    conn.sendall((str(top_1) + "," + str(top_5)).encode())
                    break
                except Exception as e:
                    print(e, 2)
                    sleep(1)

        if data == "info":
            conn.sendall(str(MODEL_PATH + "," + str(SIZE)).encode())

    conn.close()
