import os
import math
import time
from Client import Client
from Peer import Peer
import streamlit as st
import multiprocessing

chunk_SIZE = 512 * 1024
placeholder = st.empty()


def calculate_number_of_chunk(file_path):
    file_size = os.path.getsize(file_path)
    return math.ceil(file_size / chunk_SIZE)


def upload_file():
    with placeholder.form("extended_form"):
        uploaded_file = st.file_uploader("Choose Upload File")
        numPeer = st.text_input("Input number of Peer: ")
        submit_button = st.form_submit_button("Submit")

    if submit_button and uploaded_file is not None:
        fileUp = open("./Uploaded_File/" + str(uploaded_file.name), "wb")
        fileUp.write(uploaded_file.read())
        placeholder.empty()
        return (uploaded_file.name, numPeer)
    return None


def distribute_file_to_peer(file_name, num_peer):
    for i in range(1, num_peer + 1):
        os.system("mkdir Local_Peer" + str(i) +
                  " && cd Local_Peer" + str(i) + " && mkdir Chunk_List")
        fileUpload = open("./Uploaded_File/" + str(file_name), "rb")
        fileDistribute = open("./Local_Peer" + str(i) +
                              "/" + str(file_name), "wb")
        fileDistribute.write(fileUpload.read())


upload = upload_file()
if upload is not None:
    fileName = str(upload[0])
    peerNum = int(upload[1])
    chunkNum = calculate_number_of_chunk("./Original_File/" + str(fileName))
    distribute_file_to_peer(fileName, peerNum)

    peerList = []
    for i in range(1, peerNum + 1):
        peer = Peer("127.0.0.1", 12008 + i, i, "Local_Peer" + str(i))
        peer.file_break(fileName)
        peerList.append(peer)

    for peer in peerList:
        peer.start()

    time.sleep(2)
    client = multiprocessing.Process(target=Client.Client_Process, args=(
        Client, fileName, peerNum, "127.0.0.1", 12008, chunkNum))
    client.start()
