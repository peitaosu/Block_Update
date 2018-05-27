import os, hashlib

def get_file_blocks_dict(dir_path, block_size):
    file_dict = {}
    for item in os.walk(dir_path):
        if os.path.isfile(item):
            file_dict[item] = get_blocks_hash(item, block_size)
    return file_dict

def get_blocks_hash(file_path, block_size):
    f = open(file_path)
    hash_list = []
    while True:
        data = f.read(block_size)
        if not data:
            break
        hash_list.add(hashlib.md5(data).hexdigest())
    return hash_list
