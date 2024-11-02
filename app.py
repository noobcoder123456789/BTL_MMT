import os
import socket
import streamlit as st
import threading
from BackEnd.PeerBackEnd import Peer
from BackEnd.ClientBackEnd import Client
from BackEnd.Helper import get_wireless_ipv4, list_shared_files, chunk_SIZE, tracker_url

# CONSTANT


peerID = Peer.get_peers_count(tracker_url) + 1
port = 12000 + peerID - 1
files_path = './BackEnd/Share_File'

# CLASS


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
            thread = threading.Thread(target=self.download, args=(
                self, serverIPs[i - 1], startChunk, endChunk, serverPorts[i - 1], i))
            threads.append(thread)
            startChunk = endChunk + 1
            thread.start()

        for thread in threads:
            thread.join()

        print("Finished processing all servers.")

        self.file_make(self, fileName)


# UI

st.set_page_config(layout="wide", page_title="HCMUTorrent")

upload = False
col1, col2, col3 = st.columns(3)

with col1:
    tab1, tab2 = st.tabs(["Client", "Peer"])

    with tab1:
        my_client = MyClient(str(get_wireless_ipv4()), "Local_Client")

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
                torrent_data = (
                    my_client.read_torrent_file(uploaded_file.read()))
            else:
                torrent_data = (my_client.parse_magnet_link(magnet_link))

            fileName = torrent_data["hashinfo"]["file_name"]
            tracker_url = str(torrent_data["announce"])
            chunkNum = torrent_data["hashinfo"]["num_chunks"]
            serverName, serverPort = my_client.get_peers_with_file(
                tracker_url, fileName)
            peerNum = len(serverName)

            for i in range(peerNum):
                clientSocket = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM)
                clientSocket.connect((serverName[i], serverPort[i]))
                clientSocket.send(fileName.encode('utf-8'))
                clientSocket.close()

            my_client.Client_Process(fileName, peerNum, serverName,
                                     serverPort, chunkNum)

            st.success("Download completed successfully")

    with tab2:

        st.header("Upload File")

        with st.form("extended_form_2", clear_on_submit=True):
            uploaded_files = st.file_uploader(
                "Choose Upload File Which", accept_multiple_files=True)
            submit_button = st.form_submit_button("Submit")

        if submit_button:
            if uploaded_files:
                for uploaded_file in uploaded_files:
                    file_path = os.path.join(files_path, uploaded_file.name)
                    if os.path.exists(file_path):
                        st.warning(
                            f"File {uploaded_file.name} already exists and was skipped.")
                        continue
                    with open(file_path, "wb") as fileUp:
                        fileUp.write(uploaded_file.read())
                upload = True
            else:
                st.error(
                    "No files were uploaded. Please select files to upload.")

with col2:
    st.header("Your file")
    shared_files = list_shared_files(files_path)
    for file in shared_files:
        st.text(file)

with col3:
    if upload:
        peer = Peer(str(get_wireless_ipv4()), port, peerID, "Share_File")
        st.text("Joining the swarm...")

        current_files = [file for file in os.listdir(
            files_path) if os.path.isfile(os.path.join(files_path, file))]
        peer.announce_to_tracker(tracker_url, current_files)
        st.text("Listening....")

        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSocket.bind(("", port))
        serverSocket.listen(20)
        connectionSocket, addr = serverSocket.accept()
        fileName = connectionSocket.recv(1024).decode('utf-8')
        print("File which client request:", fileName)
        peer.file_break(fileName)
        peer.start(serverSocket)
