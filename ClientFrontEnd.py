import socket
import streamlit as st
from BackEnd.Helper import get_wireless_ipv4
from BackEnd.ClientBackEnd import Client
import time
import os


class MyClient(Client):
    def recv_all(self, sock, size):
        data = b''
        while len(data) < size:
            packet = sock.recv(size - len(data))
            if not packet:
                break
            data += packet
        return data

    def start(self, serverIP, startChunk, endChunk, serverPort, peerID):
        def recv_all(sock, size):
            data = b''
            while len(data) < size:
                packet = sock.recv(size - len(data))
                if not packet:
                    break
                data += packet
            return data

        # def progress_bar(current, total, bar_length=50):
        #     progress = current / total
        #     block = int(bar_length * progress)
        #     bar = "#" * block + "-" * (bar_length - block)
        #     percent = round(progress * 100, 2)
        #     sys.stdout.write(f"\rDownloading: [{bar}] {percent}%")
        #     sys.stdout.flush()

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
            # progress_bar(chunk - startChunk + 1, endChunk - startChunk + 1)
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

    def Client_Process(self, fileName, peerNum, serverIPs, serverPorts, chunkNum, progress_bars):
        print(f"Processing file: {fileName}")
        print(f"Number of peers: {peerNum}")

        for idx, (serverIP, serverPort) in enumerate(zip(serverIPs, serverPorts)):
            print(f"Connecting to server {serverIP}:{serverPort}")

            clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                clientSocket.connect((serverIP, serverPort))
                request = "Request for chunk from Peer"
                clientSocket.send(request.encode('utf-8'))

                # Example communication
                response = clientSocket.recv(1024).decode('utf-8')
                print(f"Server response: {response}")

                # Define the range of chunks this peer will handle
                # For simplicity, assume equal distribution
                chunks_per_peer = chunkNum // peerNum
                startChunk = idx * chunks_per_peer
                endChunk = (idx + 1) * chunks_per_peer - \
                    1 if idx != peerNum - 1 else chunkNum - 1

                clientSocket.send(str(startChunk).encode('utf-8'))
                clientSocket.recv(1024)  # Acknowledge
                clientSocket.send(str(endChunk).encode('utf-8'))
                clientSocket.recv(1024)  # Acknowledge

                for chunk in range(startChunk, endChunk + 1):
                    # Assuming chunk size is 1024 bytes
                    data = self.recv_all(clientSocket, 1024)
                    # Save the chunk
                    file_path = f"./BackEnd/{self.local_path}/Chunk_List/chunk{chunk}.txt"
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    with open(file_path, "wb") as fileT:
                        fileT.write(data)

                    # Update progress
                    progress = (chunk - startChunk + 1) / \
                        (endChunk - startChunk + 1)
                    progress_bars[idx].progress(progress)

                    print(
                        f"Received chunk {chunk} from {serverIP}:{serverPort}")

                print(f"Finished downloading from {serverIP}:{serverPort}")

            except Exception as e:
                print(f"Error connecting to {serverIP}:{serverPort} - {e}")
            finally:
                clientSocket.close()

        print("Finished processing all servers.")


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
        torrent_data = (Client.read_torrent_file(uploaded_file.read()))
    else:
        torrent_data = (Client.parse_magnet_link(magnet_link))

    message_placeholder.success("Upload successful")

    fileName = torrent_data["hashinfo"]["file_name"]
    tracker_url = str(torrent_data["announce"])
    chunkNum = torrent_data["hashinfo"]["num_chunks"]
    client = MyClient(str(get_wireless_ipv4()), "Local_Client")
    serverName, serverPort = client.get_peers_with_file(tracker_url, fileName)
    peerNum = len(serverName)

    progress_placeholders = []
    progress_bars = []
    for i in range(peerNum):
        peer_placeholder = st.empty()
        peer_placeholder.write(f"Peer {i+1}: {serverName[i]}:{serverPort[i]}")
        progress_bar = peer_placeholder.progress(0)
        progress_placeholders.append(peer_placeholder)
        progress_bars.append(progress_bar)

    for i in range(peerNum):
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((serverName[i], serverPort[i]))
        clientSocket.send(fileName.encode('utf-8'))
        clientSocket.close()

    client.Client_Process(fileName, peerNum, serverName,
                          serverPort, chunkNum, progress_bars)

    st.success("Download completed successfully!")

    # while len([completed_progress for completed_progress in progress if completed_progress == 1]) != peerNum:
    #     time.sleep(0.01)
    #     for i in range(peerNum):
    #         st.progress(progress[i], text=f"Peer {i}")
