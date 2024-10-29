import socket
import streamlit as st
from BackEnd.Helper import get_wireless_ipv4
from BackEnd.ClientBackEnd import Client


"""UI TỪ CHỖ NÀY"""
st.set_page_config(layout="wide", page_title="HCMUTorrent")

placeholder = st.empty()

with placeholder.form("extended_form"):
    uploaded_file = st.file_uploader("Choose a torrent file")
    st.write("Or")
    magnet_link = str(st.text_input("Magnet link: "))
    submit_button = st.form_submit_button("Submit")
"""ĐẾN CHỖ NÀY"""

"""
    Cần phải có 2 option cho người dùng:
     + Hoặc là upload .torrent file
     + Hoặc là sử dụng magnet link
    
    Phải có nút submit 

    Sau khi submit xong thì sẽ hiện ra n thanh download biểu thị cho file đang tải về :"> 
     + Phải có % tải về nha
"""

""" Dưới đây gọi BackEnd nên thôi đừng đụng nha :"> """
torrent_data = None
if submit_button:
    if uploaded_file is not None:
        torrent_data = (Client.read_torrent_file(uploaded_file.read()))
    else:
        torrent_data = (Client.parse_magnet_link(magnet_link))
    placeholder.empty()

    # torrent_data = Client.read_torrent_file(torrent_file)
    fileName = torrent_data["hashinfo"]["file_name"]
    tracker_url = str(torrent_data["announce"])
    chunkNum = torrent_data["hashinfo"]["num_chunks"]
    client = Client(str(get_wireless_ipv4()), "Local_Client")
    serverName, serverPort = client.get_peers_with_file(tracker_url, fileName)
    peerNum = len(serverName)

    for i in range(peerNum):
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((serverName[i], serverPort[i]))
        clientSocket.send(fileName.encode('utf-8'))
        # chunkNum = int(clientSocket.recv(1024).decode('utf-8'))
        clientSocket.close()

    # print("The number of chunk:", chunkNum)
    client.Client_Process(fileName, peerNum, serverName, serverPort, chunkNum)
    # process = multiprocessing.Process(target=client.Client_Process, args=(fileName, peerNum, serverName, serverPort, chunkNum))
    # process.start()
    # process.join()
