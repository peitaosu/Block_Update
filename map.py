import os, hashlib, json

class BlockMap():
    
    def __init__(self):
        self.dir_path = None
        self.block_size = 4 * 1024
        self.map = {}
    
    def set_dir_path(self, dir_path):
        self.dir_path = dir_path
    
    def set_block_size(self, block_size):
        self.block_size = block_size
    
    def get_blocks_hash(self, file_path, block_size):
        f = open(file_path)
        hash_list = []
        while True:
            data = f.read(block_size)
            if not data:
                break
            hash_list.append(hashlib.md5(data).hexdigest())
        return hash_list

    def get_blocks_map(self):
        for root, dirs, files in os.walk(self.dir_path):
            for file_item in files:
                file_path = os.path.join(root, file_item)
                self.map[file_path] = self.get_blocks_hash(file_path, self.block_size)
        return self.map
    
    def save_map(self, save_path):
        with open(save_path, "w") as save_file:
            json.dump(self.map, save_file)
