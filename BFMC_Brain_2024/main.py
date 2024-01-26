import sys

sys.path.append(".")
from multiprocessing import Queue, Event
import logging


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

# ======================================== SETTING UP ====================================
allProcesses = list()
queueList = {
    "Critical": Queue(),
    "Warning": Queue(),
    "General": Queue(),
    "Config": Queue(),
}

logging = logging.getLogger()

TrafficCommunication = False
Camera = True
PCCommunicationDemo = False
CarsAndSemaphores = False
SerialHandler = False
TestImageProcessing = True

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
