from threading import Thread
from queue import Queue
import socket


class UDPComm(Thread):
    def __init__(self, udp_ip, udp_port):
        super().__init__()
        self.__dest_addr = (udp_ip, udp_port)
        self.__outbox = Queue(1000)
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def run(self) -> None:
        while True:
            data = self.__outbox.get()
            self.__sock.sendto(data, self.__dest_addr)

    def send(self, data):
        self.__outbox.put(data)

