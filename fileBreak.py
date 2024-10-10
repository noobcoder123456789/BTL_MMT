chunk_SIZE = 512 * 1024
fileR = open("./Original_File/a.pdf", "rb")

chunk = 0
byte = fileR.read(chunk_SIZE)
while byte:
    if chunk == 0:
        print(byte)
    
    fileT = open("./Splitted_File/chunk" + str(chunk) + ".txt", "wb")
    fileT.write(byte)
    fileT.close()
    byte = fileR.read(chunk_SIZE)
    chunk += 1