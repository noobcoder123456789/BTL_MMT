import socket

chunk_SIZE = 512 * 1024

def get_request_file(chunk):
    fileT = open("./Splitted_File/chunk" + str(chunk) + ".txt", "rb")
    data = fileT.read(chunk_SIZE)
    return data

serverPort = 12000
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind(("",serverPort))
serverSocket.listen(1)
print("The server is ready to send file")

while True:
    
    connectionSocket, addr = serverSocket.accept()    
    request = connectionSocket.recv(1024).decode('utf-8')
    
    if request == "Request for chunk":
                
        startChunk = "Start"
        connectionSocket.send(startChunk.encode('utf-8')) 
        startChunk = int(connectionSocket.recv(1024).decode('utf-8'))
                 
        endChunk = "End"
        connectionSocket.send(endChunk.encode('utf-8'))  
        endChunk = int(connectionSocket.recv(1024).decode('utf-8'))
        
        print("Start: " + str(startChunk) + ", End: " + str(endChunk))
        for chunk in range(startChunk, endChunk + 1):        
            connectionSocket.send(get_request_file(chunk))              
        connectionSocket.close()
    
    elif request == "Client Had Been Successully Received All File":
        
        print(request)
        success = "All chunk are received"
        connectionSocket.send(success.encode('utf-8'))
        connectionSocket.close()
        serverSocket.close()
        break
