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


class MyPeer(Peer):
    def Server(self, serverSocket):

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

                for chunk in range(startChunk, endChunk + 1):
                    chunk_file_path = os.path.join(
                        'BackEnd', self.local_path, 'Chunk_List', f"chunk{chunk}.txt")
                    with open(chunk_file_path, "rb") as fileT:
                        data = fileT.read(chunk_SIZE)
                        connectionSocket.sendall(data)
                connectionSocket.close()

            elif request == "Client had been successully received all file":
                print("Peer" + str(self.peerID) + ":",
                      request + "from Peer" + str(self.peerID))
                success = "All chunk are received from Peer" + str(self.peerID)
                connectionSocket.send(success.encode('utf-8'))
                connectionSocket.close()
                serverSocket.close()
                break

    def start(self, serverSocket):
        st.text("Sẵn sàng gửi file")
        thread = threading.Thread(
            target=self.Server, args=(serverSocket,))
        thread.start()
        thread.join()
        os.system('cmd /c "cd BackEnd/Share_File & rmdir /s /q Chunk_List"')


class MyClient(Client):

    def download(self, serverIP, startChunk, endChunk, serverPort, peerID, logs):
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
            file_path = os.path.join(
                'BackEnd', self.local_path, 'Chunk_List', f"chunk{chunk}.txt")

            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "wb") as fileT:
                fileT.write(data)
            logs.append(f"Nhận chunk {chunk} từ peer {peerID}")

        clientSocket.close()
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((serverIP, serverPort))
        request = "Client had been successully received all file"
        clientSocket.send(request.encode('utf-8'))
        print("Client:", clientSocket.recv(1024).decode('utf-8'))
        clientSocket.close()

    def Client_Process(self, fileName, peerNum, serverIPs, serverPorts, chunkNum):
        logs = []
        st.text(f"Đang tải {fileName} từ {peerNum} peer")

        local_client_chunk_path = os.path.join(
            'BackEnd', 'Local_Client', 'Chunk_List')
        os.makedirs(local_client_chunk_path, exist_ok=True)
        chunkForEachPeer = chunkNum // peerNum

        startChunk = 0
        threads = []
        for i in range(1, peerNum + 1):
            endChunk = (
                chunkNum - 1) if i == peerNum else (startChunk + chunkForEachPeer - 1)
            st.write("Nhận chunk " + str(startChunk) +
                     " đến chunk " + str(endChunk) + " từ Peer " + str(i))
            thread = threading.Thread(target=self.download, args=(
                serverIPs[i - 1], startChunk, endChunk, serverPorts[i - 1], i, logs))
            threads.append(thread)
            startChunk = endChunk + 1
            thread.start()

        for thread in threads:
            thread.join()

        self.file_make(fileName)
        return logs


# UI

st.set_page_config(layout="wide", page_title="HCMUTorrent")

selected_tab = st.radio("", ["Client", "Peer"], horizontal=True)

col1, col2, col3 = st.columns([1, 1, 1])

if selected_tab == "Client":
    with col1:
        st.header("Download")

        my_client = MyClient(str(get_wireless_ipv4()), "Local_Client")

        placeholder = st.empty()
        message_placeholder = st.empty()

        with placeholder.form("extended_form"):
            uploaded_file = st.file_uploader("Choose a torrent file")
            st.text("Or")
            magnet_link = str(st.text_input("Magnet link: "))
            submit_button = st.form_submit_button("Submit")

    with col2:
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

            logs = my_client.Client_Process(fileName, peerNum, serverName,
                                            serverPort, chunkNum)
            for log in logs:
                st.write(log)

            st.success("Hoàn tất tải xuống")

elif selected_tab == "Peer":
    with col1:
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
                            f"{uploaded_file.name} đã tồn tại")
                        continue
                    with open(file_path, "wb") as fileUp:
                        fileUp.write(uploaded_file.read())
                upload = True
                st.success("Tải file thành công")
            else:
                st.error(
                    "Hãy chọn file để tải lên")

    with col2:
        if 'upload' not in st.session_state:
            st.session_state.upload = False

        if submit_button:
            if uploaded_files:
                st.session_state.upload = True
            else:
                st.session_state.upload = False

        if st.session_state.upload:
            peer = MyPeer(str(get_wireless_ipv4()), port, peerID, "Share_File")
            st.text("Tham gia vào mạng...")

            current_files = [file for file in os.listdir(
                files_path) if os.path.isfile(os.path.join(files_path, file))]
            peer.announce_to_tracker(tracker_url, current_files)
            st.text("Đang đợi kết nối...")

            serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            serverSocket.bind(("", port))
            serverSocket.listen(20)
            connectionSocket, addr = serverSocket.accept()
            st.write(f"Đã kết nối đến {addr[0]}")
            fileName = connectionSocket.recv(1024).decode('utf-8')
            st.text(f"File được yêu cầu gửi: {fileName}")
            peer.file_break(fileName)
            peer.start(serverSocket)
            st.text("Gửi file thành công")
            st.text("Đóng kết nối TCP")

with col3:
    st.header("Your Files")
    shared_files = list_shared_files(files_path)
    for file in shared_files:
        st.text(file)
