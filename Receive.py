import socket
import struct
UDP_IP = "192.168.1.1"
UDP_PORT = 55555

sock = socket.socket(socket.AF_INET,
                    socket.SOCK_DGRAM) #UDP
sock.bind((UDP_IP, UDP_PORT))

while True:
    data, addr = sock.recvfrom(4096) # buffer size
    s = struct.Struct('d d d')
    unpacked_data = s.unpack(data)
    print(f"Received message: {unpacked_data[0]}, {unpacked_data[1]}, {unpacked_data[2]}")