import psutil
import socket


def get_wireless_ipv4():
    for interface, addrs in psutil.net_if_addrs().items():
        if "Wi-Fi" in interface or "Wireless" in interface or "wlan" in interface:
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    return addr.address
    return None
