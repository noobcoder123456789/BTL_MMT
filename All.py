import os
import socket
import threading
import streamlit as st

# CONST 
chunk_SIZE = 512 * 1024

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

def fileBreak():    
    fileR = open("./Original_File/a.pdf", "rb")

    chunk = 0
    byte = fileR.read(chunk_SIZE)
    while byte:
        if chunk == 0:
            print(byte)
        
        fileT = open("./Splitted_File/chunk" + str(chunk) + ".txt", "wb")
        fileT.write(byte)
        fileT.close()
        byte = fileR.read(chunk_SIZE)
        chunk += 1

def fileMake():
    SplitNum = 0    
    dir_path = r'./Splitted_File'
    fileM = open("./Original_File/aCopy.pdf", "wb")    
    for path in os.listdir(dir_path):
        SplitNum += os.path.isfile(os.path.join(dir_path, path)) is True

    for chunk in range(SplitNum):
        fileT = open("./Splitted_File/chunk" + str(chunk) + ".txt", "rb")
        byte = fileT.read(chunk_SIZE)
        fileM.write(byte)

    fileM.close()

def uploadFile():
    with st.form("extended_form"):
        uploaded_file = st.file_uploader("Choose Upload File")
        submit_button = st.form_submit_button("Submit")
    
    if submit_button and uploaded_file is not None:
        fileUp = open("./Uploaded_File/" + str(uploaded_file.name), "wb")
        fileUp.write(uploaded_file.read())

# Example usage:
if __name__ == "__main__":
    node1 = Peer("127.0.0.1", 8000)
    node1.start()

    node2 = Peer("127.0.0.1", 8001)
    node2.start()

    # Give some time for nodes to start listening
    import time
    time.sleep(2)

    node2.connect("127.0.0.1", 8000)
    time.sleep(1)  # Allow connection to establish    
    node2.send_data("Hello from node2")