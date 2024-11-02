from flask import Flask, request, jsonify, send_from_directory, url_for
from tracker import Tracker
import os

app = Flask(__name__)

peers = dict()
files_download = dict()

MyTracker = Tracker(tracker_url="192.168.92.101:18000")


@app.route('/announce', methods=['POST'])
def announce():
    data = request.json
    ip = data.get('ip')
    port = data.get('port')
    files = data.get('files')

    for file in files:
        file_path = os.path.join(MyTracker.upload_folder, file)
        if not os.path.isfile(file_path):
            return jsonify({"error": f"File '{file}' does not exist on the server."}), 400
        torrent_data = MyTracker.create_torrent_data(file)
        magnet_link = MyTracker.create_magnet_link(torrent_data)
        torrent_file_path = MyTracker.create_torrent_file(torrent_data)
        # files_download[file] = {
        #     'magnet_link': magnet_link, 'torrent_file_content': torrent_file_content}
        # Construct URLs
        torrent_file_url = url_for('download_torrent', filename=os.path.basename(
            torrent_file_path), _external=True)
        files_download[file] = {
            'magnet_link': magnet_link,
            'torrent_file_url': torrent_file_url
        }

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


@app.route('/files', methods=['GET'])
def list_files():
    """List all uploaded files with their magnet links and torrent file URLs."""
    response = {}
    for file, info in files_download.items():
        response[file] = {
            'magnet_link': info['magnet_link'],
            'torrent_file_url': info['torrent_file_url']
        }
    return jsonify(response), 200


@app.route('/torrent_files/<path:filename>', methods=['GET'])
def download_torrent(filename):
    """Serve the torrent file for download."""
    return send_from_directory(MyTracker.torrent_folder, filename, as_attachment=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=18000)
