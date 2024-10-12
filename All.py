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

    def Client(serverIP, startChunk, endChunk, serverPort):    
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((serverIP, serverPort))
        request = "Request for chunk from Peer"
        print(request)

        clientSocket.send(request.encode('utf-8'))
        request = clientSocket.recv(1024).decode('utf-8')
        clientSocket.send(str(startChunk).encode('utf-8'))
        clientSocket.send(str(endChunk).encode('utf-8'))

        for chunk in range(startChunk, endChunk + 1):
            data = clientSocket.recv(chunk_SIZE)
            fileT = open("./Chunk_List/chunk" + str(chunk) + ".txt", "wb")
            fileT.write(data)
            fileT.close()
        clientSocket.close()

        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((serverIP, serverPort))
        request = "Client had been successully received all file"
        clientSocket.send(request.encode('utf-8'))
        print(clientSocket.recv(1024).decode('utf-8'))
        clientSocket.close()

    def Server(peerPort, peerNum):
        serverPort = peerPort
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSocket.bind(("",serverPort))
        serverSocket.listen(1)
        print("The Peer" + str(peerNum) + " is ready to send file")
        
        while True:
            connectionSocket, addr = serverSocket.accept()    
            request = connectionSocket.recv(1024).decode('utf-8')
            
            if request == "Request for chunk from Peer":                    
                startChunk = "Start"
                connectionSocket.send(startChunk.encode('utf-8')) 
                startChunk = int(connectionSocket.recv(1024).decode('utf-8'))
                        
                endChunk = "End"
                connectionSocket.send(endChunk.encode('utf-8'))  
                endChunk = int(connectionSocket.recv(1024).decode('utf-8'))
                
                for chunk in range(startChunk, endChunk + 1):  
                    fileT = open("./Splitted_File/chunk" + str(chunk) + ".txt", "rb")
                    data = fileT.read(chunk_SIZE)      
                    connectionSocket.sendall(data)              
                connectionSocket.close()
            
            elif request == "Client had been successully received all file":            
                print(request + "from Peer" + str(peerNum))
                success = "All chunk are received from Peer" + str(peerNum)
                connectionSocket.send(success.encode('utf-8'))
                connectionSocket.close()
                serverSocket.close()            
                print("Peer" + str(peerNum) + " has successully sent all file")
                print("Peer" + str(peerNum) + "'s TCP connection close.")
                break


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
