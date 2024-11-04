import psutil
import socket
import os
import math
import requests

chunk_SIZE = 512 * 1024
tracker_url = "http://10.130.124.6:18000"


def get_wireless_ipv4():
    for interface, addrs in psutil.net_if_addrs().items():
        if "Wi-Fi" in interface or "Wireless" in interface or "wlan" in interface:
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    return addr.address
    return None


def list_shared_files(files_path):
    return [file for file in os.listdir(files_path) if os.path.isfile(os.path.join(files_path, file))]


def calculate_number_of_chunk(file_size):
    return math.ceil(file_size / chunk_SIZE)


def get_peers_count(tracker_url):
    response = requests.get(tracker_url + '/peers_count')
    if response.status_code == 200:
        peer_count = response.json().get('peer_count', 0)
        return peer_count
