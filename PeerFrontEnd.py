import os
import socket
import streamlit as st
from BackEnd.PeerBackEnd import Peer

def get_file_wish_to_share(folder_path):
    files_in_folder = os.listdir(folder_path)
    files = [f for f in files_in_folder if os.path.isfile(os.path.join(folder_path, f))]
    return files

tracker_url = "http://10.130.229.64:5000"
peerID = Peer.get_peers_count(tracker_url) + 1
port = 12000 + peerID - 1

"""UI TỪ CHỖ NÀY"""
upload = False
placeholder = st.empty()
with placeholder.form("extended_form"):
    uploaded_files = st.file_uploader("Choose Upload File Which ", accept_multiple_files=True)
    submit_button = st.form_submit_button("Submit")

if submit_button and uploaded_files is not None:
    for uploaded_file in uploaded_files:
        fileUp = open("./BackEnd/Share_File/" + str(uploaded_file.name), "wb")
        fileUp.write(uploaded_file.read())
    placeholder.empty()
    upload = True
"""ĐẾN CHỖ NÀY"""

"""
    Lưu ý:
        + Phải giữ lại biến upload để tui check xem file đã được upload chưa
        + Sở dĩ phải cần upload là vì: khi một Peer mới tham gia vào mạng P2P này cần phải thông báo cho Tracker biết 
        nó muốn share file nào. Ko phải file nào cũng có thể share đặc biệt là mấy tài liệu mật các thứ =))))))
        + Yêu cầu cho phép upload multiple file và phải có nút submit nhen :">
        + Upload xong thì print ra màn hình là đã thành công đăng ký vào P2P xD chèn meme con mồn lèo vào càng tốt =)))
"""

""" Dưới đây gọi BackEnd nên thôi đừng đụng nha :"> """
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