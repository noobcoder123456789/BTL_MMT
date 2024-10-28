from flask import Flask, request, jsonify

# Tạo ứng dụng Flask
app = Flask(__name__)

# Lưu trữ danh sách các peer và các file của họ
peers = {
    '192.168.1.12': ['a.pdf', 'b.pdf'],
    '192.168.1.13': ['a.pdf']
}

# API để đăng ký peer và file của peer đó
@app.route('/announce', methods=['POST'])
def announce():
    data = request.json
    ip = data.get('ip')
    files = data.get('files')

    if ip and files:
        peers[ip] = files
        return jsonify({"message": "Peer registered successfully"}), 200
    return jsonify({"error": "Invalid data"}), 400

# API để lấy danh sách peer có chứa file được yêu cầu
@app.route('/peers', methods=['GET'])
def get_peers():
    file_name = request.args.get('file')
    if file_name:
        matching_peers = [ip for ip, files in peers.items() if file_name in files]
        return jsonify({"peers": matching_peers}), 200
    return jsonify({"error": "File not specified"}), 400

# API mới để lấy số lượng peer đã đăng ký
@app.route('/peers_count', methods=['GET'])
def get_peers_count():
    peer_count = len(peers)
    return jsonify({"peer_count": peer_count}), 200

# Chạy máy chủ tracker
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
