import os
import sys
import math
import time
import socket
import threading
import streamlit as st
import multiprocessing

chunk_SIZE = 512 * 1024
placeholder = st.empty()

def calculate_number_of_chunk(file_path):
    file_size = os.path.getsize(file_path)
    return math.ceil(file_size / chunk_SIZE)

def upload_file():
    with placeholder.form("extended_form"):
        uploaded_file = st.file_uploader("Choose Upload File")        
        numPeer = st.text_input("Input number of Peer: ")
        submit_button = st.form_submit_button("Submit")
    
    if submit_button and uploaded_file is not None:
        fileUp = open("./Uploaded_File/" + str(uploaded_file.name), "wb")        
        fileUp.write(uploaded_file.read())
        placeholder.empty()
        return (uploaded_file.name, numPeer)
    return None

def distribute_file_to_peer(file_name, num_peer):    
    for i in range(1, num_peer + 1):
        os.system("mkdir Local_Peer" + str(i) + " && cd Local_Peer" + str(i) + " && mkdir Chunk_List")
        fileUpload = open("./Uploaded_File/" + str(file_name), "rb") 
        fileDistribute = open("./Local_Peer" + str(i) + "/" + str(file_name), "wb")
        fileDistribute.write(fileUpload.read())

class Peer():
    def __init__(self, host, port, peerNum, local_path):
        self.host = host
        self.port = port
        self.peerNum = peerNum
        self.local_path = local_path
    
    def Server(self):
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSocket.bind(("", self.port))
        serverSocket.listen(1)
        print("Peer" + str(self.peerNum) + ":", "The Peer" + str(self.peerNum) + " is ready to send file")
        
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
                    fileT = open("./" + str(self.local_path) + "/Chunk_List/chunk" + str(chunk) + ".txt", "rb")
                    data = fileT.read(chunk_SIZE)      
                    connectionSocket.sendall(data)      
                connectionSocket.close()
            
            elif request == "Client had been successully received all file":            
                success = "All chunk are received from Peer" + str(self.peerNum)
                connectionSocket.send(success.encode('utf-8'))
                connectionSocket.close()
                serverSocket.close()            
                print("Peer" + str(self.peerNum) + ":", "Peer" + str(self.peerNum) + " has successully sent all file")
                print("Peer" + str(self.peerNum) + ":", "Peer" + str(self.peerNum) + "'s TCP connection close.")
                break

    def file_break(self, file_name):
        fileR = open("./" + str(self.local_path) + "/" + str(file_name), "rb")

        chunk = 0
        byte = fileR.read(chunk_SIZE)
        while byte:
            # if chunk == 0:
            #     print(byte)
            
            fileT = open("./" + str(self.local_path) + "/Chunk_List/chunk" + str(chunk) + ".txt", "wb")
            fileT.write(byte)
            fileT.close()
            byte = fileR.read(chunk_SIZE)
            chunk += 1

    def start(self):
        thread = threading.Thread(target=Peer.Server, args=(self,))
        thread.start()

class Client():
    def __init__(self, host, port, local_path):
        self.host = host
        self.port = port        
        self.local_path = local_path
        os.system("mkdir " + str(local_path) + " && cd " + str(local_path) + " && mkdir Chunk_List")

    def Client(self, serverIP, startChunk, endChunk, serverPort):   
        def recv_all(sock, size):
            data = b''
            while len(data) < size:
                packet = sock.recv(size - len(data))
                if not packet:
                    break
                data += packet
            return data        
         
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((serverIP, serverPort))
        request = "Request for chunk from Peer"

        clientSocket.send(request.encode('utf-8'))
        request = clientSocket.recv(1024).decode('utf-8')
        clientSocket.send(str(startChunk).encode('utf-8'))
        request = clientSocket.recv(1024).decode('utf-8')
        clientSocket.send(str(endChunk).encode('utf-8'))
        
        for chunk in range(startChunk, endChunk + 1):
            data = recv_all(clientSocket, chunk_SIZE)
            fileT = open("./" + str(self.local_path) + "/Chunk_List/chunk" + str(chunk) + ".txt", "wb")
            fileT.write(data)
            fileT.close()
        clientSocket.close()

        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((serverIP, serverPort))
        request = "Client had been successully received all file"
        clientSocket.send(request.encode('utf-8'))
        print("Client:", clientSocket.recv(1024).decode('utf-8'))
        clientSocket.close()

    def file_make(self, file_name):        
        SplitNum = 0   
        dir_path = "./" + str(self.local_path) + "/Chunk_List"
        for path in os.listdir(dir_path):
            SplitNum += os.path.isfile(os.path.join(dir_path, path)) is True

        fileM = open("./" + str(self.local_path) + "/" + str(file_name), "wb")
        for chunk in range(SplitNum):
            fileT = open(str(dir_path) + "/chunk" + str(chunk) + ".txt", "rb")
            byte = fileT.read(chunk_SIZE)
            fileM.write(byte)

        fileM.close()
        print("Client: Merge all chunk completely")

    def Client_Process(self, fileName, peerNum, serverIP, serverPort, chunkNum):
        self.local_path = "Local_Client"
        os.system("mkdir Local_Client && cd Local_Client && mkdir Chunk_List")
        chunkForEachPeer = chunkNum // peerNum
        startChunk = 0
        threads = []
        for i in range(1, peerNum + 1):
            endChunk = (chunkNum - 1) if i == peerNum else (startChunk + chunkForEachPeer - 1)
            print("Client: Request chunk" + str(startChunk) + " to chunk" + str(endChunk) + " from Peer" + str(i))
            thread = threading.Thread(target=Client.Client, args=(self, serverIP, startChunk, endChunk, serverPort + i))
            threads.append(thread)
            startChunk = endChunk + 1
            thread.start()
        
        for thread in threads:
            thread.join()
        
        Client.file_make(self, fileName)

upload = upload_file()
if upload is not None:
    fileName = str(upload[0])
    peerNum = int(upload[1])
    chunkNum = calculate_number_of_chunk("./Original_File/" + str(fileName))
    distribute_file_to_peer(fileName, peerNum)

    peerList = []
    for i in range(1, peerNum + 1):
        peer = Peer("127.0.0.1", 12008 + i, i, "Local_Peer" + str(i))
        peer.file_break(fileName)
        peerList.append(peer)

    for peer in peerList:
        peer.start()
    
    time.sleep(2)
    client = multiprocessing.Process(target=Client.Client_Process, args=(Client, fileName, peerNum, "127.0.0.1", 12008, chunkNum))
    client.start()
