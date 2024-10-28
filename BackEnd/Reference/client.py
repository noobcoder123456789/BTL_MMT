import os
import json
import requests

# Thông tin peer
peer_ip = '192.168.1.12'
port = 12000

def get_file_wish_to_share(folder_path):
    files_in_folder = os.listdir(folder_path)
    files = [f for f in files_in_folder if os.path.isfile(os.path.join(folder_path, f))]
    return files

def get_peers_count(tracker_url):
    response = requests.get(tracker_url + '/peers_count')
    if response.status_code == 200:
        peer_count = response.json().get('peer_count', 0)
        # print(f"Số lượng peer đã đăng ký: {peer_count}")
        return peer_count
    else:
        print(f"Lỗi khi lấy số lượng peer: {response.text}")

# Đăng ký peer với tracker
def announce_to_tracker(tracker_url, files):
    data = {
        'ip': peer_ip,
        'port': port,
        'files': files
    }
    response = requests.post(tracker_url + '/announce', json=data)
    if response.status_code == 200:
        print("Đăng ký thành công với tracker")
    else:
        print(f"Lỗi khi đăng ký với tracker: {response.text}")

if __name__ == '__main__':
    tracker_url = 'http://192.168.1.13:5000'  # Thay đổi URL thành URL của tracker
    files = get_file_wish_to_share('../Original_File')
    announce_to_tracker(tracker_url, files)