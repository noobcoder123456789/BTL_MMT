import os
import socket
import threading
import streamlit as st

class Peer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connections = []

    def connect(self, peer_host, peer_port):
        # print(f"My host: {self.host}")
        connection = socket.create_connection((peer_host, peer_port))

        self.connections.append(connection)
        print(f"Connected to {peer_host}:{peer_port}")

    def listen(self):
        self.socket.bind((self.host, self.port))
        self.socket.listen(10)
        print(f"Listening for connections on {self.host}:{self.port}")

        while True:
            connection, address = self.socket.accept()
            self.connections.append(connection)
            print(f"Accepted connection from {address}")
            threading.Thread(target=self.handle_client, args=(connection, address)).start()

    def send_data(self, data):
        for connection in self.connections:
            try:
                connection.sendall(data.encode())
            except socket.error as e:
                print(f"Failed to send data. Error: {e}")
                self.connections.remove(connection)

    def handle_client(self, connection, address):
        while True:
            try:
                data = connection.recv(1024)
                if not data:
                    break
                print(f"Received data from {address}: {data.decode()}")
            except socket.error:
                break

        print(f"Connection from {address} closed.")
        self.connections.remove(connection)
        connection.close()

    def start(self):
        listen_thread = threading.Thread(target=self.listen)
        listen_thread.start()

    def TCP_Client(self, host, port):
        print("TCP Clienttttttttttttttttttttttttttttttt")
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((host, port))
        # sentence = input("Input lowercase sentence:")
        sentence = "yo what the fack men?"
        clientSocket.send(sentence.encode())
        modifiedSentence = clientSocket.recv(1024)
        print("From Server: ", modifiedSentence.decode()) 
        clientSocket.close()
    
    def TCP_Server(self):
        self.port = 12000
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSocket.bind(("",self.port))
        serverSocket.listen(1)
        print("The server is ready to receive")
        while True:
            connectionSocket, addr = serverSocket.accept()
            sentence = connectionSocket.recv(1024).decode()
            capitalizedSentence = sentence.upper()
            connectionSocket.send(capitalizedSentence.encode()) 
            connectionSocket.close()

    def get_request_file(start, end):
        listOfChunk = list()
        for chunk in range(start, end + 1):
            fileT = open("./Splitted_File/chunk" + str(chunk) + ".txt", "rb")
            listOfChunk.append(fileT)
        
        return listOfChunk

if __name__ == "__main__":
    node1 = Peer("127.0.0.1", 8000)
    node1.start()

    node2 = Peer("127.0.0.1", 8001)
    node2.start()

    # Give some time for nodes to start listening
    import time

    time.sleep(2)
    node1.TCP_Server()
    time.sleep(2)

    node2.TCP_Client("127.0.0.1", 8000)
    time.sleep(1)  # Allow connection to establish    
    node2.send_data("Hello from node2")