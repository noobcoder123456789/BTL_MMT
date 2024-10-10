import os
chunk_SIZE = 512 * 1024

fileM = open("./Original_File/aCopy.pdf", "wb")

SplitNum = 0
dir_path = r'./Splitted_File'
for path in os.listdir(dir_path):
    SplitNum += os.path.isfile(os.path.join(dir_path, path)) is True

for chunk in range(SplitNum):
    fileT = open("./Splitted_File/chunk" + str(chunk) + ".txt", "rb")
    byte = fileT.read(chunk_SIZE)
    fileM.write(byte)

fileM.close()