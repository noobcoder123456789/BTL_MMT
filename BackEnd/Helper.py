import psutil
import socket
import os
import math

chunk_SIZE = 512 * 1024
tracker_url = "http://192.168.1.8:18000"


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
