import socket
import time
import threading

chunk_SIZE = 512 * 1024

class Peer():
    def Client(serverIP, startChunk, endChunk, serverPort, threadNum):    
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
        print(request + str(threadNum) + " from chunk" + str(startChunk) + " to chunk" + str(endChunk))
        print("Client is current listenning to port: ", serverPort)

        clientSocket.send(request.encode('utf-8'))
        request = clientSocket.recv(1024).decode('utf-8')
        clientSocket.send(str(startChunk).encode('utf-8'))
        request = clientSocket.recv(1024).decode('utf-8')
        clientSocket.send(str(endChunk).encode('utf-8'))

        for chunk in range(startChunk, endChunk + 1):
            data = recv_all(clientSocket, chunk_SIZE)
            fileT = open("./Local/chunk" + str(chunk) + ".txt", "wb")
            print("Received chunk" + str(chunk) + ".txt")
            fileT.write(data)
            fileT.close()
        clientSocket.close()

        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((serverIP, serverPort))
        request = "Client had been successully received all file"
        clientSocket.send(request.encode('utf-8'))
        print(clientSocket.recv(1024).decode('utf-8'))
        clientSocket.close()

num_clients = 2
threads = []
startList = [0, 33]
endList = [32, 65]
peerPortList = [12000, 12001]

for i in range(num_clients):
    thread = threading.Thread(target=Peer.Client, args=("127.0.0.1", startList[i], endList[i], peerPortList[i], i))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()