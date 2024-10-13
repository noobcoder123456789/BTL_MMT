import os
chunk_SIZE = 512 * 1024

SplitNum = 0
dir_path = './Local'
# dir_path = './Splitted_File'
for path in os.listdir(dir_path):
    SplitNum += os.path.isfile(os.path.join(dir_path, path)) is True

fileM = open("./Original_File/aCopy.pdf", "wb")
for chunk in range(0, SplitNum):
    fileT = open(dir_path + "/chunk" + str(chunk) + ".txt", "rb")
    byte = fileT.read(chunk_SIZE)
    fileM.write(byte)

fileM.close()