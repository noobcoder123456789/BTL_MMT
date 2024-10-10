import socket
import pickle
chunk_SIZE = 512 * 1024
serverName = "127.0.0.1"
serverPort = 12000
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect((serverName, serverPort))
data = clientSocket.recv(1024)
receivedChunkList = pickle.loads(data)
for chunk in range(len(receivedChunkList)):
    fileT = open("./Chunk_List/chunk" + str(chunk) + ".txt", "rb")
    byte = receivedChunkList[chunk].read(chunk_SIZE)
    fileT.write(byte)
clientSocket.close()