import socket
import threading

chunk_SIZE = 512 * 1024

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
                print("Peer" + str(self.peerNum) + ":", request + "from Peer" + str(self.peerNum))
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
            fileT = open("./" + str(self.local_path) + "/Chunk_List/chunk" + str(chunk) + ".txt", "wb")
            fileT.write(byte)
            fileT.close()
            byte = fileR.read(chunk_SIZE)
            chunk += 1

    def start(self):
        thread = threading.Thread(target=Peer.Server, args=(self,))
        thread.start()