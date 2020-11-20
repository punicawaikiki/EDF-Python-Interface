import socket
UDP_IP = "192.168.1.1"
UDP_PORT = 55555

sock = socket.socket(socket.AF_INET,
                    socket.SOCK_DGRAM) #UDP
sock.bind((UDP_IP, UDP_PORT))

while True:
    data, addr = sock.recvfrom(4096) # buffer size
    print(f"Received message: {data.decode('ascii')}")