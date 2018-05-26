import os, hashlib

def get_file_list(dir_path):
    file_list = []
    for item in os.walk(dir_path):
        if os.path.isfile(item):
            file_list.add(item)
    return file_list

def get_blocks_hash(file_path, block_size):
    f = open(file_path)
    hash_list = []
    while True:
        data = f.read(block_size)
        if not data:
            break
        hash_list.add(hashlib.md5(data).hexdigest())
    return hash_list
