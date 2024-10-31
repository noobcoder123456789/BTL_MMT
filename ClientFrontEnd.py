import socket
import streamlit as st
from BackEnd.Helper import get_wireless_ipv4
from BackEnd.ClientBackEnd import Client
import time


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

    # torrent_data = Client.read_torrent_file(torrent_file)
    fileName = torrent_data["hashinfo"]["file_name"]
    tracker_url = str(torrent_data["announce"])
    chunkNum = torrent_data["hashinfo"]["num_chunks"]
    client = Client(str(get_wireless_ipv4()), "Local_Client")
    print("Truoc")
    serverName, serverPort = client.get_peers_with_file(tracker_url, fileName)
    print("Sau")
    peerNum = len(serverName)
    progress = []

    for i in range(peerNum):
        progress.append(0)
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((serverName[i], serverPort[i]))
        clientSocket.send(fileName.encode('utf-8'))
        # chunkNum = int(clientSocket.recv(1024).decode('utf-8'))
        clientSocket.close()

    # print("The number of chunk:", chunkNum)
    client.Client_Process(fileName, peerNum, serverName,
                          serverPort, chunkNum, progress)
    while len([completed_progress for completed_progress in progress if completed_progress == 1]) != peerNum:
        time.sleep(0.01)
        for i in range(peerNum):
            st.progress(progress[i], text=f"Peer {i}")
    # process = multiprocessing.Process(target=client.Client_Process, args=(fileName, peerNum, serverName, serverPort, chunkNum))
    # process.start()
    # process.join()
