import os
import socket
import streamlit as st
from BackEnd.PeerBackEnd import Peer
from BackEnd.Helper import get_wireless_ipv4


def get_file_wish_to_share(folder_path):
    files_in_folder = os.listdir(folder_path)
    files = [f for f in files_in_folder if os.path.isfile(
        os.path.join(folder_path, f))]
    return files


ip = get_wireless_ipv4()
tracker_url = "http://10.130.11.102:5000"
peerID = Peer.get_peers_count(tracker_url) + 1
port = 12000 + peerID - 1


files_path = './BackEnd/Share_File'
upload = False

st.set_page_config(layout="wide", page_title="HCMUTorrent")

col1, col2 = st.columns(2)

placeholder = st.empty()
with col1:
    st.header("Upload File")
    placeholder = st.empty()
    with placeholder.form("extended_form"):
        uploaded_files = st.file_uploader(
            "Choose Upload File Which", accept_multiple_files=True)
        submit_button = st.form_submit_button("Submit")

    if submit_button and uploaded_files is not None:
        for uploaded_file in uploaded_files:
            fileUp = open("./BackEnd/Share_File/" +
                          str(uploaded_file.name), "wb")
            fileUp.write(uploaded_file.read())
            fileUp.close()
        upload = True

with col2:
    st.header("Your file")
    files = [file for file in os.listdir(
        files_path) if os.path.isfile(os.path.join(files_path, file))]
    for file in files:
        st.text(file)


if upload is True:
    peer = Peer(str(Peer.get_wireless_ipv4()), port, peerID, "Share_File")
    files = get_file_wish_to_share("./BackEnd/Share_File")
    print("Joining to swarm....")
    peer.announce_to_tracker(tracker_url, files)

    print("Listening....")
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind(("", port))
    serverSocket.listen(1)
    connectionSocket, addr = serverSocket.accept()
    fileName = connectionSocket.recv(1024).decode('utf-8')
    # chunkNum = calculate_number_of_chunk("./Share_File/" + fileName)
    # connectionSocket.send(str(chunkNum).encode('utf-8'))
    # connectionSocket.close()
    print("File which client request:", fileName)
    peer.file_break(fileName)
    peer.start(serverSocket)
