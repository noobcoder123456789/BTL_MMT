import os
import math
import hashlib

chunk_SIZE = 512 * 1024


def calculate_number_of_chunk(file_path):
    file_size = os.path.getsize(file_path)
    return math.ceil(file_size / chunk_SIZE)


def create_magnet_link(torrent_data):
    tracker_url = torrent_data['announce'].decode('utf-8')
    file_name = torrent_data['hashinfo']['file_name']
    num_chunks = torrent_data['hashinfo']['num_chunks']
    chunk_size = torrent_data['hashinfo']['chunk_size']
    file_size = torrent_data['hashinfo']['file_size']
    hashinfo_str = f"{file_name}{chunk_size}{num_chunks}"
    info_hash = hashlib.sha1(hashinfo_str.encode('utf-8')).hexdigest()
    magnet_link = (
        f"magnet:?xt=urn:btih:{info_hash}"
        f"&dn={file_name}"
        f"&tr={tracker_url}"
        f"&x.n={num_chunks}"
        f"&x.c={chunk_size}"
        f"&x.s={file_size}"
    )

    return magnet_link


file_name = "a.pdf"
file_path = "./Share_File/" + file_name
num_chunks = calculate_number_of_chunk(file_path)
tracker_url = "http://192.168.92.101:18000"
file_size = os.path.getsize(file_path)
torrent_data = {
    'announce': tracker_url.encode('utf-8'),
    'hashinfo': {
        'file_name': file_name,
        'num_chunks': num_chunks,
        'chunk_size': chunk_SIZE,
        'file_size': file_size
    }
}

magnet_link = create_magnet_link(torrent_data)
print("Magnet Link:", magnet_link)
