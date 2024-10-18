import socket

chunk_SIZE = 512 * 1024
serverName = "127.0.0.1"
serverPort = 12000
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect((serverName, serverPort))
request = "Request for chunk"
print(request)

clientSocket.send(request.encode('utf-8'))
request = clientSocket.recv(1024).decode('utf-8')

startChunk = 0
clientSocket.send(str(startChunk).encode('utf-8'))

endChunk = 15
clientSocket.send(str(endChunk).encode('utf-8'))

for chunk in range(startChunk, endChunk + 1):

    data = clientSocket.recv(chunk_SIZE)
    fileT = open("./Chunk_List/chunk" + str(chunk) + ".txt", "wb")
    fileT.write(data)
    fileT.close()

clientSocket.close()

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect((serverName, serverPort))
request = "Client Had Been Successully Received All File"
clientSocket.send(request.encode('utf-8'))
print(clientSocket.recv(1024).decode('utf-8'))
clientSocket.close()