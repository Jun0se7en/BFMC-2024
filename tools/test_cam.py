import cv2

import onnxruntime
import numpy as np
import time
import os
import sys
import math

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from lib.control.UITCar import UITCar

session = onnxruntime.InferenceSession("./models/SEG/model-032.onnx", providers=['CUDAExecutionProvider'])

input_name = session.get_inputs()[0].name
output_name = session.get_outputs()[0].name
input_shape = session.get_inputs()[0].shape
input_type = session.get_inputs()[0].type

CHECKPOINT = 380
LANEWIGHT = 55            # Độ rộng đường (pixel)
IMAGESHAPE = [640, 400]      # Kích thước ảnh Input model 
def AngCal(image):
    
    # print(image.shape)
    # image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = image.reshape((400, 640))
    h, w = image.shape

    line_row = image[CHECKPOINT, :]
    center = image[h-5, :]
    
    flag = True
    center_min_x = 0
    center_max_x = 0
    
    for x, y in enumerate(center):
        if y == 255 and flag:
            flag = False
            center_min_x = x
        elif y == 255:
            center_max_x = x
            
    center_segment = int((center_max_x+center_min_x)/2)
    x0, y0 = center_segment, h-1
    

    flag = True
    min_x = 0
    max_x = 0
    
    for x, y in enumerate(line_row):
        if y == 255 and flag:
            flag = False
            min_x = x
        elif y == 255:
            max_x = x

    center_row = int((max_x+min_x)/2)
    # gray = cv2.circle(gray, (center_row, CHECKPOINT), 1, 90, 2)
    # cv2.imshow('test', gray)
    
    # x0, y0 = int(w/2), h
    x1, y1 = center_row, CHECKPOINT
    
    image=cv2.line(image,(x1, y1),(x0, y0),(0,0,0),2)

    value = (x1-x0)/(y0-y1)

    angle = int(math.degrees(math.atan(value)))

    # print(steering)
    
    if angle > 60:
        angle = 60
    elif angle < -60:
        angle = -60
    elif angle in range(0,11):
        angle = 0
	# _lineRow = image[CHECKPOINT, :] 
	# count = 0
	# sumCenter = 0
	# centerArg = int(IMAGESHAPE[0]/2)
	# minx=0
	# maxx=0
	# first_flag=True
	# for x, y in enumerate(_lineRow):
	# 	if y == 255 and first_flag:
	# 		first_flag=False
	# 		minx=x
	# 	elif y == 255:
	# 		maxx=x
	 
	# # centerArg = int(sumCenter/count)
	# centerArg=int((minx+maxx)//2)
	# count=maxx-minx

	# # print(minx,maxx,centerArg)
	# # print(centerArg, count)

    # if (count < LANEWIGHT):
    #     if (centerArg < int(IMAGESHAPE[0]/2)):
    #         centerArg -= LANEWIGHT - count
    #     else:
    #         centerArg += LANEWIGHT - count

	# image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

	# _steering = math.degrees(math.atan((centerArg - int(IMAGESHAPE[0]/2))/(IMAGESHAPE[1]-CHECKPOINT)))
	# # print(_steering,"----------",count)
	# image=cv2.line(image,(centerArg,CHECKPOINT),(int(IMAGESHAPE[0]/2),IMAGESHAPE[1]),(255,0,0),1)
    return angle, image

def overlay_mask(original_img, mask):

    # Resize mask để có kích thước giống ảnh gốc
    resized_mask = cv2.resize(mask, (original_img.shape[1], original_img.shape[0]), interpolation=cv2.INTER_LINEAR)

    # Chuyển đổi mask thành ảnh 3 kênh để so sánh với ảnh gốc
    mask_color = cv2.cvtColor(resized_mask, cv2.COLOR_GRAY2BGR)

    # Áp dụng mask lên ảnh gốc
    overlaid_img = cv2.addWeighted(original_img, 1, mask_color, 0.5, 0)

    # return overlaid_img
    
    # cv2.imshow('Pred', overlaid_img)
    # cv2.waitKey(0)
    cv2.imwrite(os.path.join("cam/overlay.jpg"), overlaid_img)

############################ Extract Road ###################################
bg = None
# Để tính trung bình chạy qua nền
def run_avg(image,aweight):
    # Khởi tạo nền
    global bg
    if bg is None:
        bg=image.copy().astype("float")
        return
    cv2.accumulateWeighted(image,bg,aweight)

# Phân tách đường
def extract_road(image,threshold=25):
    global bg
    diff=cv2.absdiff(bg.astype("uint8"),image)
    thresh=cv2.threshold(diff,threshold,255,cv2.THRESH_BINARY)[1]
    (cnts,_)=cv2.findContours(thresh,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

    if(len(cnts)==0):
        return
    else:
        max_cont=max(cnts,key=cv2.contourArea)
        return (thresh,max_cont)
def filter_mask(mask, threshold=200):
    # Tạo một mask mới với giá trị True cho các pixel lớn hơn 200
    filtered_mask = mask < threshold

    # Gán giá trị False cho các pixel không thỏa mãn điều kiện
    mask[filtered_mask] = 0

    return mask
    
aWeight=0.5
# t,r,b,l=0,640,240,0
num_frames=0
#############################################################################

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

    # car = UITCar()


    while 1:
        start = time.time()
        _, frame = cap.read()
        if frame is not None:
            clone = frame.copy()
            roi=frame[320:,:]
            gray=cv2.cvtColor(roi,cv2.COLOR_BGR2GRAY)
            gray=cv2.GaussianBlur(gray,(7,7),0)
            if(num_frames<30):
                run_avg(gray,aWeight)
            else:
                hand=extract_road(gray)
                if hand is not None:
                    thresh,max_cont=hand
                    mask=cv2.drawContours(clone,[max_cont+(0,320)],-1, (0, 0, 255))
                    mask=np.zeros(thresh.shape,dtype="uint8")
                    cv2.drawContours(mask,[max_cont],-1,255,-1)
                    mask = cv2.medianBlur(mask, 5)
                    mask = cv2.addWeighted(mask, 0.5, mask, 0.5, 0.0)
                    kernel = np.ones((5, 5), np.uint8)
                    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
                    res=cv2.bitwise_and(roi,roi,mask=mask)
                    res=cv2.cvtColor(res,cv2.COLOR_BGR2GRAY)
                    high_thresh, thresh_im = cv2.threshold(res, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                    lowThresh = 0.5 * high_thresh
                    hand=cv2.bitwise_and(gray,gray,mask=thresh)
                    # final = np.hstack((thresh, hand))
                    hand = filter_mask(hand,150)
                    res = cv2.Canny(hand, lowThresh, high_thresh)
                    # cdstP = cv2.cvtColor(res, cv2.COLOR_GRAY2BGR)
                    # linesP = cv2.HoughLinesP(cdstP, 1, np.pi / 180, 80, None, 80, 30)
            
                    # if linesP is not None:
                    #     for i in range(0, len(linesP)):
                    #         l = linesP[i][0]
                    #         cv2.line(cdstP, (l[0], l[1]), (l[2], l[3]), (0,0,255), 3, cv2.LINE_AA)
                    cv2.imwrite('cam/road.jpg', hand)
                    cv2.imwrite('cam/canny.jpg', res)
            num_frames += 1
            # print('Hello')