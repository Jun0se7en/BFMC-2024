# Copyright (c) 2019, Bosch Engineering Center Cluj and BFMC organizers
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE

if __name__ == "__main__":
    import sys

    sys.path.insert(0, "../../..")

from src.templates.workerprocess import WorkerProcess
from multiprocessing import Pipe
import socket
import pickle
import cv2
import base64
import numpy as np
import struct

from src.server.threads.threadServer import threadServer


class processServer(WorkerProcess):
    """This process handle camera.\n
    Args:
            queueList (dictionar of multiprocessing.queues.Queue): Dictionar of queues where the ID is the type of messages.
            logging (logging object): Made for debugging.
            debugging (bool, optional): A flag for debugging. Defaults to False.
    """

    # ====================================== INIT ==========================================
    def __init__(self, queueList, logging, debugging=False):
        print('Initializing Server Process!!!')
        self.queuesList = queueList
        self.logging = logging
        pipeRecv, pipeSend = Pipe(duplex=False)
        self.pipeRecv = pipeRecv
        self.pipeSend = pipeSend
        self.debugging = debugging
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.hostname = '192.168.2.152'
        self.port = 1234
        self.socket.bind((self.hostname, self.port))
        print(self.hostname)
        super(processServer, self).__init__(self.queuesList)
        print('Initialized Server Process Sucessfully!!!')

    # ===================================== STOP ==========================================
    def stop(self):
        """Function for stopping threads and the process."""
        # for thread in self.threads:
        #     thread.stop()
        #     thread.join()
        self.socket.close()
        super(processServer, self).stop()

    # ===================================== RUN ==========================================
    def run(self):
        """Apply the initializing methods and start the threads."""
        self.socket.listen(5)
        print("Waiting for connection...")
        
        while self._running:
            clientsocket, Address = self.socket.accept()
            print(f'IP Address [{Address}] has connect to the server!!!')
            ServerTh = threadServer(self.pipeRecv, self.pipeSend, self.queuesList, self.logging, clientsocket, Address, self, self.debugging)
            ServerTh.start()


            # cv2.imwrite("./test/cam.jpg", image)
        ServerTh.stop()
        self.socket.close()
    # ===================================== INIT TH ======================================

