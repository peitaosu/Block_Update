import os, sys, hashlib, json, shutil, optparse

class BlockMap():
    
    def __init__(self):
        self.dir_path = None
        self.diff_path = "diff"
        self.diff_file = "diff.json"
        self.block_size = 4 * 1024
        self.map = {}
        self.diff = None
    
    def set_dir_path(self, dir_path):
        self.dir_path = dir_path
    
    def set_diff_path(self, diff_path):
        self.diff_path = diff_path
    
    def set_diff_file(self, diff_file):
        self.diff_file = diff_file

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
                file_real_path = os.path.join(root, file_item)
                file_rel_path = file_real_path.lstrip(self.dir_path).lstrip("/")
                self.map[file_rel_path] = self.get_blocks_hash(file_real_path, self.block_size)
        return self.map
    
    def save_map(self, save_path):
        with open(save_path, "w") as save_file:
            json.dump(self.map, save_file)
    
    def diff_map(self, target):
        if self.block_size != target.block_size:
            print "Cannot diff because block maps created with different block size."
            return None
        self.diff = {
            "added": [],
            "removed": [],
            "updated": {}
        }
        self.diff["added"] = [i for i in self.map if i not in target.map]
        self.diff["removed"] = [i for i in target.map if i not in self.map]
        same = [i for i in self.map if i in target.map]
        for i in same:
            if self.map[i] == target.map[i]:
                continue
            length = max(len(self.map[i]), len(target.map[i]))
            self.diff["updated"][i] = []
            for x in range(length):
                try:
                    if self.map[i][x] == target.map[i][x]:
                        self.diff["updated"][i].append({})
                    else:
                        self.diff["updated"][i].append({
                            "target": target.map[i][x],
                            "upgrade": self.map[i][x]
                        })
                except IndexError:
                    if x < len(self.map[i]):
                        self.diff["updated"][i].append({
                            "target": "",
                            "upgrade": self.map[i][x]
                        })
                    else:
                        self.diff["updated"][i].append({
                            "target": target.map[i][x],
                            "upgrade": ""
                        })

    def create_diff(self):
        if self.diff is None:
            return False
        for add_file in self.diff["added"]:
            source = os.path.join(self.dir_path, add_file)
            dest = os.path.join(self.diff_path, add_file)
            if not os.path.isdir(os.path.dirname(dest)):
                os.makedirs(os.path.dirname(dest))
            shutil.copyfile(source, dest)
        for update_file in self.diff["updated"]:
            upgrade_file = os.path.join(self.dir_path, update_file)
            upgrade_diff = os.path.join(self.diff_path, update_file)
            if not os.path.isdir(os.path.dirname(upgrade_diff)):
                os.makedirs(os.path.dirname(upgrade_diff))
            length = len(self.diff["updated"][update_file])
            with open(upgrade_file, "rb") as in_file:
                for i in range(length):
                    data = in_file.read(self.block_size)
                    if "upgrade" in self.diff["updated"][update_file][i] and self.diff["updated"][update_file][i]["upgrade"] != "":
                        diff_file = upgrade_diff + "-" + self.diff["updated"][update_file][i]["upgrade"]
                        with open(diff_file, 'wb') as out_file:
                            out_file.write(data)
                    else:
                        continue
        diff_file_path = os.path.join(os.path.dirname(self.diff_path), self.diff_file)
        with open(diff_file_path, "w") as save_file:
            json.dump(self.diff, save_file, indent=4)
        return True
    
def get_options():
    parser = optparse.OptionParser()
    parser.add_option("-u", "--upgrade", dest="upgrade",
                      help="upgrade folder")
    parser.add_option("-t", "--target", dest="target",
                      help="target folder")
    parser.add_option("-b", "--block", dest="block", default=4*1024, type="int",
                      help="block size")
    parser.add_option("-d", "--diff", dest="diff", default="diff",
                      help="diff output path")
    (options, args) = parser.parse_args()
    if not options.upgrade or not options.target:
        parser.print_help()
        sys.exit(-1)
    return options

if __name__ == "__main__":
    opt = get_options()

    upgrade = BlockMap()
    target = BlockMap()
    
    upgrade.set_dir_path(opt.upgrade)
    target.set_dir_path(opt.target)

    upgrade.set_block_size(opt.block)
    target.set_block_size(opt.block)

    upgrade.get_blocks_map()
    target.get_blocks_map()
    
    upgrade.diff_map(target)
    upgrade.set_diff_path(opt.diff)
    upgrade.create_diff()