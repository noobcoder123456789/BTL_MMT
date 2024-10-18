import os
import sys
import time
import socket
import threading
import multiprocessing

chunk_SIZE = 512 * 1024

class Client():
    def __init__(self, host, port, local_path):
        self.host = host
        self.port = port        
        self.local_path = local_path
        os.system("mkdir " + str(local_path) + " && cd " + str(local_path) + " && mkdir Chunk_List")

    def Client(self, serverIP, startChunk, endChunk, serverPort, peerID):   
        def recv_all(sock, size):
            data = b''
            while len(data) < size:
                packet = sock.recv(size - len(data))
                if not packet:
                    break
                data += packet
            return data

        def progress_bar(current, total, bar_length=50):
            progress = current / total
            block = int(bar_length * progress)
            bar = "#" * block + "-" * (bar_length - block)
            percent = round(progress * 100, 2)
            sys.stdout.write(f"\rDownloading: [{bar}] {percent}%")
            sys.stdout.flush()
         
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((serverIP, serverPort))
        request = "Request for chunk from Peer"
        # print("Client:", request)

        clientSocket.send(request.encode('utf-8'))
        request = clientSocket.recv(1024).decode('utf-8')
        clientSocket.send(str(startChunk).encode('utf-8'))
        request = clientSocket.recv(1024).decode('utf-8')
        clientSocket.send(str(endChunk).encode('utf-8'))

        for chunk in range(startChunk, endChunk + 1):
            # print('.', end='', flush=True)
            progress_bar(chunk - startChunk + 1, endChunk - startChunk + 1)
            data = recv_all(clientSocket, chunk_SIZE)
            fileT = open("./" + str(self.local_path) + "/Chunk_List/chunk" + str(chunk) + ".txt", "wb")
            fileT.write(data)
            fileT.close()
        print('')
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
        os.system('cmd /c "mkdir Local_Client & cd Local_Client & mkdir Chunk_List"')
        chunkForEachPeer = chunkNum // peerNum
        startChunk = 0
        threads = []
        for i in range(1, peerNum + 1):
            endChunk = (chunkNum - 1) if i == peerNum else (startChunk + chunkForEachPeer - 1)
            print("Client: Request chunk" + str(startChunk) + " to chunk" + str(endChunk) + " from Peer" + str(i))
            thread = threading.Thread(target=Client.Client, args=(self, serverIP[i - 1], startChunk, endChunk, serverPort[i - 1], i))
            threads.append(thread)
            startChunk = endChunk + 1
            thread.start()
        
        for thread in threads:
            thread.join()
        
        Client.file_make(self, fileName)

peerNum = 2 # OUTPUT của phần tracker
fileName = "a.pdf" # OUTPUT của phần tracker
serverName = ["192.168.1.13", "192.168.88.130"] # OUTPUT của phần tracker
serverPort = [12000, 12001]
chunkNum = 0
for i in range(peerNum):
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((serverName[i], serverPort[i]))
    clientSocket.send(fileName.encode('utf-8'))
    chunkNum = int(clientSocket.recv(1024).decode('utf-8'))    
    clientSocket.close()

print("The number of chunk:", chunkNum)
client = Client("172.0.0.1", serverPort[0], "Local_Client")
client.Client_Process(fileName, peerNum, serverName, serverPort, chunkNum)
# process = multiprocessing.Process(target=client.Client_Process, args=(fileName, peerNum, serverName, serverPort, chunkNum))
# process.start()
# process.join()
