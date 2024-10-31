import os
import sys
import socket
import bencodepy
import psutil
import requests
import threading
from urllib.parse import urlparse, parse_qs

chunk_SIZE = 512 * 1024


class Client():

    def __init__(self, host, local_path):
        self.host = host
        self.local_path = local_path
        os.system("cd BackEnd && mkdir " + str(local_path) + " && cd " +
                  str(local_path) + " && mkdir Chunk_List")

    def get_peers_with_file(self, tracker_url, file_name):
        print("Truoc")
        response = requests.get(tracker_url + '/peers',
                                params={'file': file_name})
        print("Sau")
        if response.status_code == 200:
            peers = response.json().get('peers', [])
            # print(f"Các peer có file {file_name}:")
            resIP = []
            resPort = []
            for peer in peers:
                # print(f"IP: {peer['ip']}, Port: {peer['port']}")
                resIP.append(peer['ip'])
                resPort.append(peer['port'])
            return (resIP, resPort)
        else:
            print(f"Lỗi khi lấy danh sách peer: {response.text}")

    def read_torrent_file(encoded_data):
        # with open(torrent_file, 'rb') as f:
        #     encoded_data = f.read()

        torrent_data = {}
        decoded_data = bencodepy.decode(encoded_data)
        for key, value in decoded_data.items():
            if isinstance(value, bytes):
                torrent_data[key.decode('utf-8')] = value.decode('utf-8')
            elif isinstance(value, dict):
                sub_dict = {}
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, bytes):
                        sub_dict[sub_key.decode(
                            'utf-8')] = sub_value.decode('utf-8')
                    else:
                        sub_dict[sub_key.decode('utf-8')] = sub_value
                torrent_data[key.decode('utf-8')] = sub_dict
            else:
                torrent_data[key.decode('utf-8')] = value

        return torrent_data

    def parse_magnet_link(magnet_link):
        parsed = urlparse(magnet_link)
        if parsed.scheme != 'magnet':
            raise ValueError("This is not a valid magnet link!")

        params = parse_qs(parsed.query)
        info_hash = params.get('xt', [None])[0]
        if info_hash and info_hash.startswith('urn:btih:'):
            info_hash = info_hash[9:]

        file_name = params.get('dn', [None])[0]
        tracker_url = params.get('tr', [None])[0]
        num_chunks = int(params.get('x.n', [0])[0])
        chunk_size = int(params.get('x.c', [0])[0])
        file_size = int(params.get('x.s', [0])[0])
        torrent_data = {
            'announce': tracker_url if tracker_url else None,
            'hashinfo': {
                'file_name': file_name,
                'num_chunks': num_chunks,
                'chunk_size': chunk_size,
                'file_size': file_size,
                'info_hash': info_hash
            }
        }

        return torrent_data

    def start(self, serverIP, startChunk, endChunk, serverPort, peerID, progress):
        def recv_all(sock, size):
            data = b''
            while len(data) < size:
                packet = sock.recv(size - len(data))
                if not packet:
                    break
                data += packet
            return data

        def progress_bar(current, total, bar_length=50):
            progress = current / total
            block = int(bar_length * progress)
            bar = "#" * block + "-" * (bar_length - block)
            percent = round(progress * 100, 2)
            sys.stdout.write(f"\rDownloading: [{bar}] {percent}%")
            sys.stdout.flush()

        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((serverIP, serverPort))
        request = "Request for chunk from Peer"
        # print("Client:", request)

        clientSocket.send(request.encode('utf-8'))
        request = clientSocket.recv(1024).decode('utf-8')
        clientSocket.send(str(startChunk).encode('utf-8'))
        request = clientSocket.recv(1024).decode('utf-8')
        clientSocket.send(str(endChunk).encode('utf-8'))

        for chunk in range(startChunk, endChunk + 1):
            progress = float((chunk - startChunk + 1) /
                             (endChunk - startChunk + 1))
            print('.', end='', flush=True)
            progress_bar(chunk - startChunk + 1, endChunk - startChunk + 1)
            print("Received chunk" + str(chunk))
            data = recv_all(clientSocket, chunk_SIZE)
            fileT = open("./BackEnd/" + str(self.local_path) +
                         "/Chunk_List/chunk" + str(chunk) + ".txt", "wb")
            fileT.write(data)
            fileT.close()
        print('')
        clientSocket.close()

        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((serverIP, serverPort))
        request = "Client had been successully received all file"
        clientSocket.send(request.encode('utf-8'))
        print("Client:", clientSocket.recv(1024).decode('utf-8'))
        clientSocket.close()

    def file_make(self, file_name):
        SplitNum = 0
        dir_path = "./BackEnd/" + str(self.local_path) + "/Chunk_List"
        for path in os.listdir(dir_path):
            SplitNum += os.path.isfile(os.path.join(dir_path, path)) is True

        fileM = open("./BackEnd/" + str(self.local_path) +
                     "/" + str(file_name), "wb")
        for chunk in range(SplitNum):
            fileT = open(str(dir_path) + "/chunk" + str(chunk) + ".txt", "rb")
            byte = fileT.read(chunk_SIZE)
            fileM.write(byte)

        fileM.close()
        print("Client: Merge all chunk completely")

    def Client_Process(self, fileName, peerNum, serverIP, serverPort, chunkNum, progress):
        os.system(
            'cmd /c " cd BackEnd & mkdir Local_Client & cd Local_Client & mkdir Chunk_List"')
        chunkForEachPeer = chunkNum // peerNum
        startChunk = 0
        threads = []
        for i in range(1, peerNum + 1):
            endChunk = (
                chunkNum - 1) if i == peerNum else (startChunk + chunkForEachPeer - 1)
            print("Client: Request chunk" + str(startChunk) +
                  " to chunk" + str(endChunk) + " from Peer" + str(i))
            thread = threading.Thread(target=Client.start, args=(
                self, serverIP[i - 1], startChunk, endChunk, serverPort[i - 1], i, progress[i - 1]))
            threads.append(thread)
            startChunk = endChunk + 1
            thread.start()

        for thread in threads:
            thread.join()

        Client.file_make(self, fileName)
