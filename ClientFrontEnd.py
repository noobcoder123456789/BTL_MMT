import socket
import streamlit as st
from BackEnd.Helper import get_wireless_ipv4
from BackEnd.ClientBackEnd import Client
import os
import threading

chunk_SIZE = 512 * 1024


class MyClient(Client):

    def download(self, serverIP, startChunk, endChunk, serverPort, peerID):
        def recv_all(sock, size):
            data = b''
            while len(data) < size:
                packet = sock.recv(size - len(data))
                if not packet:
                    break
                data += packet
            return data

        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((serverIP, serverPort))
        request = "Request for chunk from Peer"

        clientSocket.send(request.encode('utf-8'))
        request = clientSocket.recv(1024).decode('utf-8')
        clientSocket.send(str(startChunk).encode('utf-8'))
        request = clientSocket.recv(1024).decode('utf-8')
        clientSocket.send(str(endChunk).encode('utf-8'))

        for chunk in range(startChunk, endChunk + 1):
            data = recv_all(clientSocket, chunk_SIZE)
            # Save the chunk
            file_path = f"./BackEnd/{self.local_path}/Chunk_List/chunk{chunk}.txt"
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "wb") as fileT:
                fileT.write(data)

            print(
                f"Received chunk {chunk} from {serverIP}:{serverPort}")

        print(f"Finished downloading from {serverIP}:{serverPort}")

        print('')
        clientSocket.close()
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((serverIP, serverPort))
        request = "Client had been successully received all file"
        clientSocket.send(request.encode('utf-8'))
        print("Client:", clientSocket.recv(1024).decode('utf-8'))
        clientSocket.close()

    def Client_Process(self, fileName, peerNum, serverIPs, serverPorts, chunkNum):
        print(f"Processing file: {fileName}")
        print(f"Number of peers: {peerNum}")

        os.system(
            'cmd /c "mkdir Local_Client & cd Local_Client & mkdir Chunk_List"')
        chunkForEachPeer = chunkNum // peerNum
        startChunk = 0
        threads = []
        for i in range(1, peerNum + 1):
            endChunk = (
                chunkNum - 1) if i == peerNum else (startChunk + chunkForEachPeer - 1)
            print("Client: Request chunk" + str(startChunk) +
                  " to chunk" + str(endChunk) + " from Peer" + str(i))
            thread = threading.Thread(target=MyClient.download, args=(
                self, serverIPs[i - 1], startChunk, endChunk, serverPorts[i - 1], i))
            threads.append(thread)
            startChunk = endChunk + 1
            thread.start()

        for thread in threads:
            thread.join()

        print("Finished processing all servers.")

        MyClient.file_make(self, fileName)


my_client = MyClient(str(get_wireless_ipv4()), "Local_Client")

st.set_page_config(layout="wide", page_title="HCMUTorrent")

placeholder = st.empty()
message_placeholder = st.empty()

with placeholder.form("extended_form"):
    uploaded_file = st.file_uploader("Choose a torrent file")
    st.write("Or")
    magnet_link = str(st.text_input("Magnet link: "))
    submit_button = st.form_submit_button("Submit")

torrent_data = None
if submit_button:
    if uploaded_file is not None:
        torrent_data = (my_client.read_torrent_file(uploaded_file.read()))
    else:
        torrent_data = (my_client.parse_magnet_link(magnet_link))

    message_placeholder.success("Upload successful")

    fileName = torrent_data["hashinfo"]["file_name"]
    tracker_url = str(torrent_data["announce"])
    chunkNum = torrent_data["hashinfo"]["num_chunks"]
    serverName, serverPort = my_client.get_peers_with_file(
        tracker_url, fileName)
    peerNum = len(serverName)

    for i in range(peerNum):
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((serverName[i], serverPort[i]))
        clientSocket.send(fileName.encode('utf-8'))
        clientSocket.close()

    my_client.Client_Process(fileName, peerNum, serverName,
                             serverPort, chunkNum)

    st.success("Download completed successfully")
