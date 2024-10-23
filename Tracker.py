from flask import Flask, request, jsonify

app = Flask(__name__)

peers = dict()

@app.route('/announce', methods=['POST'])
def announce():
    data = request.json
    ip = data.get('ip')
    port = data.get('port')
    files = data.get('files')

    if ip and files:
        peers[ip] = {'port': port, 'files': files}
        return jsonify({"message": "Peer registered successfully"}), 200
    return jsonify({"error": "Invalid data"}), 400

@app.route('/peers', methods=['GET'])
def get_peers():
    file_name = request.args.get('file')
    if file_name:
        matching_peers = [{'ip': ip, 'port': peer_info['port']} 
                          for ip, peer_info in peers.items() 
                          if file_name in peer_info['files']]
        return jsonify({"peers": matching_peers}), 200
    return jsonify({"error": "File not specified"}), 400

@app.route('/peers_count', methods=['GET'])
def get_peers_count():
    peer_count = len(peers)
    return jsonify({"peer_count": peer_count}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
