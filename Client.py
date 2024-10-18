import socket
import os

chunk_SIZE = 512 * 1024

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
        print("Client:", request)

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