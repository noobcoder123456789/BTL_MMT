import os
import sys
import time
import math
import socket
import threading

chunk_SIZE = 512 * 1024

def calculate_number_of_chunk(file_path):
    file_size = os.path.getsize(file_path)
    return math.ceil(file_size / chunk_SIZE)

class Peer():
    def __init__(self, host, port, peerNum, local_path):
        self.host = host
        self.port = port
        self.peerNum = peerNum
        self.local_path = local_path
    
    def Server(self, serverSocket):
        def progress_bar(current, total, bar_length=50):
            progress = current / total
            block = int(bar_length * progress)
            bar = "#" * block + "-" * (bar_length - block)
            percent = round(progress * 100, 2)
            sys.stdout.write(f"\rDownloading: [{bar}] {percent}%")
            sys.stdout.flush()

        # serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # serverSocket.bind(("", self.port))
        # serverSocket.listen(1)
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
                
                # print("Sending chunk to client", end='', flush=True)
                for chunk in range(startChunk, endChunk + 1):  
                    # print('.', end='', flush=True)
                    progress_bar(chunk - startChunk + 1, endChunk - startChunk + 1)
                    fileT = open("./" + str(self.local_path) + "/Chunk_List/chunk" + str(chunk) + ".txt", "rb")
                    data = fileT.read(chunk_SIZE)      
                    connectionSocket.sendall(data) 
                print('')             
                connectionSocket.close()
            
            elif request == "Client had been successully received all file":            
                print("Peer" + str(self.peerNum) + ":", request + "from Peer" + str(self.peerNum))
                success = "All chunk are received from Peer" + str(self.peerNum)
                connectionSocket.send(success.encode('utf-8'))
                connectionSocket.close()
                serverSocket.close()            
                print("Peer" + str(self.peerNum) + ":", "Peer" + str(self.peerNum) + " has successully sent all file")
                print("Peer" + str(self.peerNum) + ":", "Peer" + str(self.peerNum) + "'s TCP connection close.")
                break

    def file_break(self, file_name):
        os.system('cmd /c "cd ' + str(self.local_path) + ' & mkdir Chunk_List"')
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

    def start(self, serverSocket):
        thread = threading.Thread(target=Peer.Server, args=(self, serverSocket))
        thread.start()
        thread.join()
        os.system('cmd /c "cd File_List & rmdir /s /q Chunk_List"')

print("Listening....")
port = 12000
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind(("", port))
serverSocket.listen(1)
connectionSocket, addr = serverSocket.accept()
fileName = connectionSocket.recv(1024).decode('utf-8')
chunkNum = calculate_number_of_chunk("./File_List/" + fileName)
connectionSocket.send(str(chunkNum).encode('utf-8'))
# connectionSocket.close()
print("File which client request:", fileName)
peer = Peer("192.168.157.72", port, 1, "File_List")
peer.file_break(fileName)
peer.start(serverSocket)
