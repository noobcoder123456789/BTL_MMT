import os
import socket
import streamlit as st
from BackEnd.PeerBackEnd import Peer
from BackEnd.Helper import get_wireless_ipv4


tracker_url = "http://192.168.92.101:18000"
peerID = Peer.get_peers_count(tracker_url) + 1
port = 12000 + peerID - 1
files_path = './BackEnd/Share_File'


def list_shared_files():
    return [file for file in os.listdir(files_path) if os.path.isfile(os.path.join(files_path, file))]


upload = False
st.set_page_config(layout="wide", page_title="HCMUTorrent")

col1, col2, col3 = st.columns(3)

with col1:
    st.header("Upload File")

    with st.form("extended_form", clear_on_submit=True):
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
        peer = Peer(str("192.168.242.17"), port, peerID, "Share_File")
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
