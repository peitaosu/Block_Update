import os, hashlib, json

class BlockMap():
    
    def __init__(self):
        self.root_path = None
        self.dir_path = None
        self.block_size = 4 * 1024
        self.map = {}
    
    def set_root_path(self, root_path):
        self.root_path = root_path

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
        for root, dirs, files in os.walk(os.path.join(self.root_path, self.dir_path)):
            for file_item in files:
                file_real_path = os.path.join(root, file_item)
                file_rel_path = file_real_path.lstrip(self.root_path)
                self.map[file_rel_path] = self.get_blocks_hash(file_real_path, self.block_size)
        return self.map
    
    def save_map(self, save_path):
        with open(save_path, "w") as save_file:
            json.dump(self.map, save_file)
    
    def diff_map(self, target):
        if self.block_size != target.block_size:
            print "Cannot diff because block maps created with different block size."
            return None
        diff = {
            "added": [],
            "removed": [],
            "updated": {}
        }
        diff["added"] = [i for i in self.map if i not in target.map]
        diff["removed"] = [i for i in target.map if i not in self.map]
        same = [i for i in self.map if i in target.map]
        for i in same:
            if self.map[i] == target.map[i]:
                continue
            length = max(len(self.map[i]), len(target.map[i]))
            diff["updated"][i] = []
            for x in range(length):
                try:
                    if self.map[i][x] == target.map[i][x]:
                        diff["updated"][i].append({})
                    else:
                        diff["updated"][i].append({
                            "target": target.map[i][x],
                            "upgrade": self.map[i][x]
                        })
                except IndexError:
                    if x < len(self.map[i]):
                        diff["updated"][i].append({
                            "target": "",
                            "upgrade": self.map[i][x]
                        })
                    else:
                        diff["updated"][i].append({
                            "target": target.map[i][x],
                            "upgrade": ""
                        })
        return diff
