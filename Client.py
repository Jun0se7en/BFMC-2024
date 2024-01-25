import socket
import pickle
from PIL import Image
from io import BytesIO
import cv2
import struct

# Kết nối đến server
server_address = ('192.168.2.152', 1234)  # Địa chỉ và cổng của server
client_socket = socket.socket()
print(socket.gethostname())
client_socket.connect(server_address)

payload_size = struct.calcsize("Q")

# Nhận dữ liệu từ server

data = b""
while True:
    chunk = client_socket.recv(4*1024)
    if not chunk:
        break
    data+=chunk
    packed_msg_size = data[:payload_size]
    data = data[payload_size:]
    msg_size = struct.unpack("Q", packed_msg_size)[0]
    
    while len(data)<msg_size:
        data+=client_socket.recv(4*1024)
    image = data[:msg_size]
    data = data[msg_size:]
    
    image = pickle.loads(image)
    # print(image)
    cv2.imshow('frame', image)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()

# Đóng kết nối
client_socket.close()