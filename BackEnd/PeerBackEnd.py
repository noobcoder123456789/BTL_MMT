import os
import sys
# import time
import math
import psutil
import socket
import requests
import threading

chunk_SIZE = 512 * 1024

def calculate_number_of_chunk(file_path):
    file_size = os.path.getsize(file_path)
    return math.ceil(file_size / chunk_SIZE)

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

        # serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # serverSocket.bind(("", self.port))
        # serverSocket.listen(1)
        print("Peer" + str(self.peerID) + ":", "The Peer" + str(self.peerID) + " is ready to send file")
        
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
                    progress_bar(chunk - startChunk + 1, endChunk - startChunk + 1)
                    fileT = open("./" + str(self.local_path) + "/Chunk_List/chunk" + str(chunk) + ".txt", "rb")
                    data = fileT.read(chunk_SIZE)      
                    connectionSocket.sendall(data) 
                print('')             
                connectionSocket.close()
            
            elif request == "Client had been successully received all file":            
                print("Peer" + str(self.peerID) + ":", request + "from Peer" + str(self.peerID))
                success = "All chunk are received from Peer" + str(self.peerID)
                connectionSocket.send(success.encode('utf-8'))
                connectionSocket.close()
                serverSocket.close()            
                print("Peer" + str(self.peerID) + ":", "Peer" + str(self.peerID) + " has successully sent all file")
                print("Peer" + str(self.peerID) + ":", "Peer" + str(self.peerID) + "'s TCP connection close.")
                break

    def file_break(self, file_name):
        os.system('cmd /c "cd ' + str(self.local_path) + ' & mkdir Chunk_List"')
        fileR = open("./" + str(self.local_path) + "/" + str(file_name), "rb")

        chunk = 0
        byte = fileR.read(chunk_SIZE)
        while byte:
            # if chunk == 0:
            #     print(byte)
            
            fileT = open("./" + str(self.local_path) + "/Chunk_List/chunk" + str(chunk) + ".txt", "wb")
            fileT.write(byte)
            fileT.close()
            byte = fileR.read(chunk_SIZE)
            chunk += 1

    def start(self, serverSocket):
        thread = threading.Thread(target=Peer.Server, args=(self, serverSocket))
        thread.start()
        thread.join()
        os.system('cmd /c "cd Share_File & rmdir /s /q Chunk_List"')

    def get_wireless_ipv4():
        for interface, addrs in psutil.net_if_addrs().items():
            if "Wi-Fi" in interface or "Wireless" in interface or "wlan" in interface:
                for addr in addrs:
                    if addr.family == socket.AF_INET:
                        return addr.address
        return None

# tracker_url = "http://10.130.151.157:5000"
# peerID = Peer.get_peers_count(tracker_url) + 1
# port = 12000 + peerID - 1

# """UI TỪ CHỖ NÀY"""
# upload = False
# placeholder = st.empty()
# with placeholder.form("extended_form"):
#     uploaded_files = st.file_uploader("Choose Upload File Which ", accept_multiple_files=True)
#     submit_button = st.form_submit_button("Submit")

# if submit_button and uploaded_files is not None:
#     for uploaded_file in uploaded_files:
#         fileUp = open("./Share_File/" + str(uploaded_file.name), "wb")
#         fileUp.write(uploaded_file.read())
#     placeholder.empty()
#     upload = True

# if upload is True:    
#     peer = Peer(str(Peer.get_wireless_ipv4()), port, peerID, "Share_File")
#     files = get_file_wish_to_share("./Share_File")
#     print("Joining to swarm....")
#     peer.announce_to_tracker(tracker_url, files)

#     print("Listening....")
#     serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     serverSocket.bind(("", port))
#     serverSocket.listen(1)
#     connectionSocket, addr = serverSocket.accept()
#     fileName = connectionSocket.recv(1024).decode('utf-8')
#     # chunkNum = calculate_number_of_chunk("./Share_File/" + fileName)
#     # connectionSocket.send(str(chunkNum).encode('utf-8'))
#     # connectionSocket.close()
#     print("File which client request:", fileName)
#     peer.file_break(fileName)
#     peer.start(serverSocket)