import cv2
import numpy as np
import os

try:
    os.mkdir('./test/')
except:
    pass

vid = cv2.VideoCapture(0) 

if not vid.isOpened():
    raise Exception("Capture failed")

while(True): 
    ret, frame = vid.read() 

    cv2.imshow('Frame', frame)

    if not ret:
        print("read fail")
        break
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

vid.release() 
cv2.destroyAllWindows()