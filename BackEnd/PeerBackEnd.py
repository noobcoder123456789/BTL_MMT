import os
import sys
import requests
import threading

chunk_SIZE = 512 * 1024


class Peer():
    def __init__(self, IP, port, peerID, local_path):
        self.IP = IP
        self.port = port
        self.peerID = peerID
        self.local_path = local_path

    def announce_to_tracker(self, tracker_url, files):
        data = {
            'ip': self.IP,
            'port': self.port,
            'files': files
        }
        response = requests.post(tracker_url + '/announce', json=data)
        if response.status_code == 200:
            print("Successful registration with tracker")
        else:
            print(f"Error registering with tracker: {response.text}")

    def get_peers_count(tracker_url):
        response = requests.get(tracker_url + '/peers_count')
        if response.status_code == 200:
            peer_count = response.json().get('peer_count', 0)
            return peer_count

    def Server(self, serverSocket):
        def progress_bar(current, total, bar_length=50):
            progress = current / total
            block = int(bar_length * progress)
            bar = "#" * block + "-" * (bar_length - block)
            percent = round(progress * 100, 2)
            sys.stdout.write(f"\rDownloading: [{bar}] {percent}%")
            sys.stdout.flush()

        print("Peer" + str(self.peerID) + ":", "The Peer" +
              str(self.peerID) + " is ready to send file")

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

                # print("Sending chunk to client", end='', flush=True)
                for chunk in range(startChunk, endChunk + 1):
                    # print('.', end='', flush=True)
                    # print("Sending chunk:", chunk)
                    progress_bar(chunk - startChunk + 1,
                                 endChunk - startChunk + 1)
                    fileT = open("./BackEnd/" + str(self.local_path) +
                                 "/Chunk_List/chunk" + str(chunk) + ".txt", "rb")
                    # print("./BackEnd/" + str(self.local_path) +
                    #       "/Chunk_List/chunk" + str(chunk) + ".txt")
                    data = fileT.read(chunk_SIZE)
                    connectionSocket.sendall(data)
                print('')
                connectionSocket.close()

            elif request == "Client had been successully received all file":
                print("Peer" + str(self.peerID) + ":",
                      request + "from Peer" + str(self.peerID))
                success = "All chunk are received from Peer" + str(self.peerID)
                connectionSocket.send(success.encode('utf-8'))
                connectionSocket.close()
                serverSocket.close()
                print("Peer" + str(self.peerID) + ":", "Peer" +
                      str(self.peerID) + " has successully sent all file")
                print("Peer" + str(self.peerID) + ":", "Peer" +
                      str(self.peerID) + "'s TCP connection close.")
                break

    def file_break(self, file_name):
        os.system('cmd /c "cd BackEnd/' +
                  str(self.local_path) + ' & mkdir Chunk_List"')
        fileR = open("./BackEnd/" + str(self.local_path) +
                     "/" + str(file_name), "rb")

        chunk = 0
        byte = fileR.read(chunk_SIZE)
        while byte:
            fileT = open("./BackEnd/" + str(self.local_path) +
                         "/Chunk_List/chunk" + str(chunk) + ".txt", "wb")
            fileT.write(byte)
            fileT.close()
            byte = fileR.read(chunk_SIZE)
            chunk += 1

    def start(self, serverSocket):
        thread = threading.Thread(
            target=Peer.Server, args=(self, serverSocket))
        thread.start()
        thread.join()
        os.system('cmd /c "cd BackEnd/Share_File & rmdir /s /q Chunk_List"')
