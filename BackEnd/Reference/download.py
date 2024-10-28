import requests

def get_peers_with_file(tracker_url, file_name):
    response = requests.get(tracker_url + '/peers', params={'file': file_name})
    if response.status_code == 200:
        peers = response.json().get('peers', [])
        print(f"Các peer có file {file_name}:")
        res = []
        for peer in peers:
            # print(f"IP: {peer['ip']}, Port: {peer['port']}")
            res.append((peer['ip'], peer['port']))
        return res
    else:
        print(f"Lỗi khi lấy danh sách peer: {response.text}")

def get_peers_count(tracker_url):
    response = requests.get(tracker_url + '/peers_count')
    if response.status_code == 200:
        peer_count = response.json().get('peer_count', 0)
        print(f"Số lượng peer đã đăng ký: {peer_count}")
        return peer_count
    else:
        print(f"Lỗi khi lấy số lượng peer: {response.text}")

if __name__ == '__main__':
    tracker_url = 'http://192.168.1.13:5000'
    file_name = input("File name wish to find: ")
    temp = get_peers_with_file(tracker_url, file_name)
    print(type(temp))
    print(temp)
