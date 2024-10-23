import time
import socket
import threading

chunk_SIZE = 512 * 1024

class Peer:
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
                    print("Send chunk" + str(chunk) + ".txt")
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

numPeer = 2
threads = []
peerPortList = [12000, 12001]

for i in range(numPeer):
    client_thread = threading.Thread(target=Peer.Server, args=(peerPortList[i], i))
    threads.append(client_thread)
    client_thread.start()