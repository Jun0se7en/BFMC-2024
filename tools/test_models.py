import cv2
import torch
from matplotlib import pyplot as plt
import numpy as np
import os
import cv2
import itertools


def gstreamer_pipeline(
    capture_width=640,
    capture_height=640,
    display_width=640,
    display_height=640,
    framerate=20,
    flip_method=0,
):
    return (
        "nvarguscamerasrc ! "
        "video/x-raw(memory:NVMM), "
        "width=(int)%d, height=(int)%d, "
        "format=(string)NV12, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )

if __name__ == "__main__":

    cap = cv2.VideoCapture(gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)
    assert cap.isOpened(), "Camera failed"
    
    # Load Models
    OBJ_model = torch.hub.load('ultralytics/yolov5', 'custom', path='./models/OBJ/08-11-1222pm(v5).pt', force_reload=True)
    OBJ_model.conf = 0.5

    while True:
        _, frame = cap.read()
        OBJ_results = OBJ_model(frame)
        res = np.squeeze(OBJ_results.render())
        cv2.imshow('raw',frame)
        cv2.imshow('OBJ',res)
        cv2.waitKey(1)
