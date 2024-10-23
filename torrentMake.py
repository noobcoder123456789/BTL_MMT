import os
import math
import json
import hashlib
import bencodepy
from urllib.parse import urlparse, parse_qs

def create_torrent_file(file_path, file_name, tracker_url, chunk_size, output_file):
    file_size = os.path.getsize(file_path)
    num_chunks = math.ceil(file_size / chunk_size)

    torrent_data = {
        'announce': tracker_url.encode('utf-8'),
        'hashinfo': {
            'file_name': file_name,
            'num_chunks': num_chunks,
            'chunk_size': chunk_size,
            'file_size': file_size
        }
    }
    
    # Bencode the data
    encoded_data = bencodepy.encode(torrent_data)
    
    # Write the encoded data to a .torrent file
    with open(output_file, "wb") as f:
        f.write(encoded_data)
    
    print(f"Torrent file '{output_file}' created successfully!")

chunk_size = 512 * 1024
file_name = "a.pdf"
file_path = "./Share_File/" + file_name
tracker_url = "http://192.168.1.13:5000"
output_file = "./Torrent_File/a.torrent"
create_torrent_file(file_path, file_name, tracker_url, chunk_size, output_file)