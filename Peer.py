import os
import socket
import streamlit as st
from BackEnd.PeerBackEnd import Peer
from BackEnd.Helper import get_wireless_ipv4
import threading

# Configuration
tracker_url = "http://192.168.92.101:18000"
peerID = Peer.get_peers_count(tracker_url) + 1
port = 12000 + peerID - 1
files_path = './BackEnd/Share_File'

# Ensure the share directory exists
os.makedirs(files_path, exist_ok=True)

# Function to list shared files


def list_shared_files():
    return [file for file in os.listdir(files_path) if os.path.isfile(os.path.join(files_path, file))]


# Initialize Streamlit page
st.set_page_config(layout="wide", page_title="HCMUTorrent Peer")

# Initialize session state variables
if 'server_running' not in st.session_state:
    st.session_state.server_running = False
if 'server_thread' not in st.session_state:
    st.session_state.server_thread = None
if 'peer_instance' not in st.session_state:
    st.session_state.peer_instance = None

# Function to handle incoming client connections


def handle_client(peer, connectionSocket, addr):
    try:
        st.session_state.message_queue.append(
            f"Connection established with {addr}")
        # Receive the requested file name
        fileName = connectionSocket.recv(1024).decode('utf-8')
        st.session_state.message_queue.append(
            f"Client requested file: {fileName}")

        # Check if the file exists
        file_path = os.path.join(files_path, fileName)
        if os.path.exists(file_path):
            st.session_state.message_queue.append(
                f"Sending file `{fileName}` to {addr}...")
            with open(file_path, "rb") as f:
                while True:
                    data = f.read(1024)
                    if not data:
                        break
                    connectionSocket.sendall(data)
            st.session_state.message_queue.append(
                f"File `{fileName}` sent successfully to {addr}.")
        else:
            st.session_state.message_queue.append(
                f"File `{fileName}` does not exist.")

    except Exception as e:
        st.session_state.message_queue.append(
            f"Error handling client {addr}: {e}")
    finally:
        connectionSocket.close()
        st.session_state.message_queue.append(
            f"Connection with {addr} closed.")

# Function to run the server


def run_server():
    try:
        # Initialize the peer
        peer = Peer(str(get_wireless_ipv4()), port, peerID, "Share_File")
        st.session_state.peer_instance = peer
        st.session_state.message_queue.append("Joining the swarm...")

        # Announce current files to the tracker
        current_files = list_shared_files()
        peer.announce_to_tracker(tracker_url, current_files)
        st.session_state.message_queue.append("Announced to tracker.")

        # Setup server socket
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSocket.bind(("", port))
        serverSocket.listen(1)  # Listen for one connection at a time
        st.session_state.message_queue.append(
            f"Peer is listening on port {port}...")

        while st.session_state.server_running:
            st.session_state.message_queue.append(
                "Waiting for a client to connect...")
            # Set timeout to allow periodic check of server_running
            serverSocket.settimeout(1.0)
            try:
                connectionSocket, addr = serverSocket.accept()
                handle_client(peer, connectionSocket, addr)
            except socket.timeout:
                continue  # Timeout reached, loop back to check server_running flag

        serverSocket.close()
        st.session_state.message_queue.append("Server has been stopped.")

    except Exception as e:
        st.session_state.message_queue.append(
            f"Server encountered an error: {e}")
        st.session_state.server_running = False


# Create two columns: col1 for upload, col2 for shared files
col1, col2, col3 = st.columns(3)

with col1:
    st.header("Upload")

    # Initialize a message queue for thread-safe UI updates
    if 'message_queue' not in st.session_state:
        st.session_state.message_queue = []

    # File upload form
    with st.form("upload_form", clear_on_submit=True):
        uploaded_files = st.file_uploader(
            "Choose files to upload", accept_multiple_files=True)
        submit_button = st.form_submit_button("Submit")

    # Handle form submission
    if submit_button:
        if uploaded_files:
            upload_success = False  # Flag to track successful uploads
            for uploaded_file in uploaded_files:
                # Sanitize the filename to prevent directory traversal
                safe_filename = os.path.basename(uploaded_file.name)
                file_path = os.path.join(files_path, safe_filename)
                if os.path.exists(file_path):
                    st.warning(
                        f"File `{safe_filename}` already exists and was skipped.")
                    continue
                with open(file_path, "wb") as fileUp:
                    fileUp.write(uploaded_file.read())
                st.success(f"File `{safe_filename}` uploaded successfully.")
                upload_success = True
            if upload_success:
                st.info("All files uploaded successfully!")
        else:
            st.error("No files were uploaded. Please select files to upload.")

with col2:
    st.header("Your Files")
    shared_files = list_shared_files()
    if shared_files:
        for file in shared_files:
            st.text(file)

with col3:
    if list_shared_files():
        if not st.session_state.server_running:
            if st.button("Start Server"):
                st.session_state.server_running = True
                st.session_state.message_queue.append("Ready to share file")
                # Start the server in a separate thread
                st.session_state.server_thread = threading.Thread(
                    target=run_server, daemon=True)
                st.session_state.server_thread.start()
                st.experimental_rerun()  # Rerun to update the button
        else:
            if st.button("Stop Server"):
                st.session_state.server_running = False
                # st.session_state.message_queue.append("Stopping the server...")
                st.experimental_rerun()  # Rerun to update the button
    else:
        st.info("No files are shared. Please upload files to start the server.")

    # Display server messages
    if 'message_queue' in st.session_state and st.session_state.message_queue:
        #     st.subheader("Server Logs")
        for message in st.session_state.message_queue:
            st.write(message)
        st.session_state.message_queue = []
