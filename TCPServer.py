import socket
import pickle

def get_request_file(start, end):
    listOfChunk = list()
    for chunk in range(start, end + 1):
        fileT = open("./Splitted_File/chunk" + str(chunk) + ".txt", "rb")
        fileTemp.write(fileT.read())
        listOfChunk.append(fileT)
    
    return listOfChunk

serverPort = 12000
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind(("",serverPort))
serverSocket.listen(1)
print("The server is ready to send file")
while True:
    connectionSocket, addr = serverSocket.accept()
    sendChunkFileList = get_request_file(0, 65)
    sendChunkFile = pickle.dumps(sendChunkFileList)
    connectionSocket.sendall(sendChunkFile)
    connectionSocket.close()