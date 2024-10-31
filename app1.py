import os
import socket
import streamlit as st
from BackEnd.PeerBackEnd import Peer
from BackEnd.ClientBackEnd import Client
from BackEnd.Helper import get_wireless_ipv4
import time

# CONSTANT
tracker_url = "http://10.130.41.120:18000"
peerID = Peer.get_peers_count(tracker_url) + 1
port = 12000 + peerID - 1
files_path = './BackEnd/Share_File'

# FUNCTION


def list_shared_files():
    return [file for file in os.listdir(files_path) if os.path.isfile(os.path.join(files_path, file))]


st.set_page_config(layout="wide", page_title="HCMUTorrent")

tab1, tab2 = st.tabs(["Client", "Peer"])

with tab1:
    placeholder = st.empty()
    message_placeholder = st.empty()

    with placeholder.form("extended_form_1"):
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
        client = Client(str(get_wireless_ipv4()), "Local_Client")
        print("Truoc")
        serverName, serverPort = client.get_peers_with_file(
            tracker_url, fileName)
        print("Sau")
        peerNum = len(serverName)
        progress = []

        for i in range(peerNum):
            progress.append(0)
            clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            clientSocket.connect((serverName[i], serverPort[i]))
            clientSocket.send(fileName.encode('utf-8'))
            clientSocket.close()

        client.Client_Process(fileName, peerNum, serverName,
                              serverPort, chunkNum, progress)
        while len([completed_progress for completed_progress in progress if completed_progress == 1]) != peerNum:
            time.sleep(0.01)
            for i in range(peerNum):
                st.progress(progress[i], text=f"Peer {i}")

with tab2:
    upload = False
    col1, col2, col3 = st.columns(3)

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
        shared_files = list_shared_files()
        for file in shared_files:
            st.text(file)

    with col3:
        if upload:
            peer = Peer(str(Peer.get_wireless_ipv4()),
                        port, peerID, "Share_File")
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
