import os, hashlib

def get_file_blocks_dict(dir_path, block_size):
    file_dict = {}
    for root, dirs, files in os.walk(dir_path):
        for file_item in files:
            file_path = os.path.join(root, file_item)
            file_dict[file_path] = get_blocks_hash(file_path, block_size)
    return file_dict

def get_blocks_hash(file_path, block_size):
    f = open(file_path)
    hash_list = []
    while True:
        data = f.read(block_size)
        if not data:
            break
        hash_list.append(hashlib.md5(data).hexdigest())
    return hash_list
