import sys

sys.path.append(".")
from multiprocessing import Queue, Event
import logging
import torch
import os


# ===================================== PROCESS IMPORTS ==================================
from src.gateway.processGateway import processGateway
from src.hardware.camera.processCamera import processCamera
from src.hardware.serialhandler.processSerialHandler import processSerialHandler
from src.utils.PCcommunicationDemo.processPCcommunication import (
    processPCCommunicationDemo,
)
from src.utils.PCcommunicationDashBoard.processPCcommunication import (
    processPCCommunicationDashBoard,
)
from src.data.CarsAndSemaphores.processCarsAndSemaphores import processCarsAndSemaphores
from src.data.TrafficCommunication.processTrafficCommunication import (
    processTrafficCommunication,
)

from src.imageProcessing.testImageProcessing.processImageProcessing import processImageProcessing

from src.imageProcessing.objectDetection.processObjectDetection import processObjectDetection

from src.imageProcessing.laneDetection.processSegmentation import processSegmentation

from src.server.processServer import processServer

from lib.utils.utils import  ( get_cfg )

from lib.utils.plots import Colors
from lib.model.trt import trt_model

# ======================================== SETTING UP ====================================
allProcesses = list()
queueList = {
    "Critical": Queue(),
    "Warning": Queue(),
    "General": Queue(),
    "Config": Queue(),
    "Segmentation": Queue(),
}

logging = logging.getLogger()

TrafficCommunication = False
Camera = True
PCCommunicationDemo = False
CarsAndSemaphores = False
SerialHandler = False
TestImageProcessing = False
Segmentation = True
ObjectDetection = False
Server = True

# ===================================== SETUP PROCESSES ==================================

# Initializing gateway
processGateway = processGateway(queueList, logging)
allProcesses.append(processGateway)

# Initializing camera
if Camera:
    processCamera = processCamera(queueList, logging, debugging=False)
    allProcesses.append(processCamera)

# Initializing interface
# if PCCommunicationDemo:
#     processPCCommunication = processPCCommunicationDemo(queueList, logging)
#     allProcesses.append(processPCCommunication)
# else:
#     processPCCommunicationDashBoard = processPCCommunicationDashBoard(
#         queueList, logging
#     )
#     allProcesses.append(processPCCommunicationDashBoard)

# Initializing cars&sems
if CarsAndSemaphores:
    processCarsAndSemaphores = processCarsAndSemaphores(queueList)
    allProcesses.append(processCarsAndSemaphores)

# Initializing GPS
if TrafficCommunication:
    processTrafficCommunication = processTrafficCommunication(queueList, logging, 3)
    allProcesses.append(processTrafficCommunication)

# Initializing serial connection NUCLEO - > PI
if SerialHandler:
    processSerialHandler = processSerialHandler(queueList, logging)
    allProcesses.append(processSerialHandler)

if TestImageProcessing:
    processImageProcessing = processImageProcessing(queueList, logging)
    allProcesses.append(processImageProcessing)

if ObjectDetection:
    print("Initializing Yolov5 Model!!!")
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    colors = Colors()
    engine, imgsize_yolo, visualize, save_dir = get_cfg('./lib/cfg/cfg.yaml')
    yolo = trt_model(engine)
    print('...')
    yolo = yolo.half()
    yolo.warmup(imgsz=(1, 3, *imgsize_yolo))  # warmup
    print("Initialized Yolov5 Model!!!")
    processObjectDetection = processObjectDetection(queueList, logging, yolo, imgsize_yolo, device)
    allProcesses.append(processObjectDetection)

if Segmentation:
    processSegmentation = processSegmentation(queueList, logging)
    allProcesses.append(processSegmentation)

if Server:
    hostname = '192.168.0.118'
    port = 1234
    processServer = processServer(queueList, logging, hostname, port)
    allProcesses.append(processServer)

# ===================================== START PROCESSES ==================================
for process in allProcesses:
    process.daemon = True
    process.start()

# ===================================== STAYING ALIVE ====================================
blocker = Event()
try:
    blocker.wait()
except KeyboardInterrupt:
    print("\nCatching a Keyboard Interruption exception! Shutdown all processes.\n")
    for proc in allProcesses:
        print("Process stopped", proc)
        proc.stop()
        proc.join()
