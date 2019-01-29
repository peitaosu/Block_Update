import os, sys, hashlib, json, shutil, optparse

class BlockMap():
    
    def __init__(self):
        self.dir_path = None
        self.diff_path = "diff"
        self.diff_file = "diff.json"
        self.block_size = 4 * 1024
        self.diff_algorithm = "md5"
        self.map = {}
        self.diff = None
    
    def set_dir_path(self, dir_path):
        """set dir path

        args:
            dir_path (str)
        """
        self.dir_path = dir_path
    
    def set_diff_path(self, diff_path):
        """set diff path

        args:
            diff_path (str)
        """
        self.diff_path = diff_path
    
    def set_diff_file(self, diff_file):
        """set diff file

        args:
            diff file (str)
        """
        self.diff_file = diff_file

    def set_block_size(self, block_size):
        """set block size

        args:
            block_size (str)
        """
        self.block_size = block_size
    
    def set_diff_algorithm(self, diff_algorithm):
        """set diff algorithm

        args:
            diff_algorithm (str)
        """
        if diff_algorithm not in dir(hashlib):
            print("Only support algorithm which supported by hashlib.")
            sys.exit(-1)
        self.diff_algorithm = diff_algorithm
    
    def _get_hash(self, data):
        """get hash of data

        args:
            data (binary)
        
        returns:
            hash (str)
        """
        return getattr(hashlib, self.diff_algorithm)(data).hexdigest()

    def _get_blocks_hash(self, file_path):
        """get hash of blocks

        args:
            file_path (str)
        
        returns:
            hash_list (list)
        """
        f = open(file_path, "rb")
        hash_list = []
        while True:
            data = f.read(self.block_size)
            if not data:
                break
            hash_list.append(self._get_hash(data))
        return hash_list

    def get_blocks_map(self):
        """get map of blocks

        returns:
            map (dict)
        """
        for root, dirs, files in os.walk(self.dir_path):
            for file_item in files:
                file_real_path = os.path.join(root, file_item)
                file_rel_path = file_real_path.lstrip(self.dir_path).lstrip("/")
                self.map[file_rel_path] = self._get_blocks_hash(file_real_path)
        return self.map
    
    def save_map(self, map_path):
        """save map to file

        args:
            map_path (str)
        """
        with open(map_path, "w") as out_file:
            json.dump(self.map, out_file, indent=4)
    
    def read_map(self, map_path):
        """read map from file

        args:
            map_path (str)
        """
        with open(map_path) as in_file:
            self.map = json.load(in_file)

    def save_diff(self, diff_path):
        """save diff to file

        args:
            diff_path (str)
        """
        with open(diff_path, "w") as out_file:
            json.dump(self.diff, out_file, indent=4)
    
    def read_diff(self, diff_path):
        """read diff from file

        args:
            diff_path (str)
        """
        with open(diff_path) as in_file:
            self.diff = json.load(in_file)
        
    def diff_map(self, target):
        """diff with target

        args:
            target (BlockMap)
        """
        if self.block_size != target.block_size:
            print("Cannot diff because block maps created with different block size.")
            sys.exit(-1)
        if self.diff_algorithm != target.diff_algorithm:
            print("Cannot diff because block maps created with different diff algorithm.")
            sys.exit(-1)
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
        """create diff
        """
        if self.diff is None:
            return False
        self.diff["block"] = self.block_size
        self.diff["algorithm"] = self.diff_algorithm
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
                        with open(diff_file, "wb") as out_file:
                            out_file.write(data)
                    else:
                        continue
        diff_file_path = os.path.join(os.path.dirname(self.diff_path), self.diff_file)
        self.save_diff(diff_file_path)
        return True

    def apply_diff(self, target):
        """apply diff

        args:
            target (BlockMap)
        """
        if self.diff is None:
            diff_file_path = os.path.join(os.path.dirname(self.diff_path), self.diff_file)
            self.read_diff(diff_file_path)
            self.block_size = self.diff["block"]
            self.diff_algorithm = self.diff["algorithm"]
        for add_file in self.diff["added"]:
            source = os.path.join(self.diff_path, add_file)
            dest = os.path.join(target.dir_path, add_file)
            if not os.path.isdir(os.path.dirname(dest)):
                os.makedirs(os.path.dirname(dest))
            shutil.copyfile(source, dest)
        for rm_file in self.diff["removed"]:
            dest = os.path.join(target.dir_path, rm_file)
            os.remove(dest)
        for update_file in self.diff["updated"]:
            target_file = os.path.join(target.dir_path, update_file)
            target_file_tmp = os.path.join(target.dir_path, update_file + ".tmp")
            upgrade_diff = os.path.join(self.diff_path, update_file)
            length = len(self.diff["updated"][update_file])
            with open(target_file_tmp, "wb") as out_file:
                with open(target_file, "rb") as in_file:
                    for i in range(length):
                        if self.diff["updated"][update_file][i] == {}:
                            data = in_file.read(self.block_size)
                            out_file.write(data)
                            continue
                        if self.diff["updated"][update_file][i]["upgrade"] != "":
                            if self.diff["updated"][update_file][i]["target"] != "":
                                data = in_file.read(self.block_size)
                                if self.diff["updated"][update_file][i]["target"] != self._get_hash(data):
                                    print("Target block hash value not match.")
                                    return False
                            diff_file = upgrade_diff + "-" + self.diff["updated"][update_file][i]["upgrade"]
                            with open(diff_file, "rb") as diff_file:
                                diff_data = diff_file.read()
                                out_file.write(diff_data)
            os.remove(target_file)
            os.rename(target_file_tmp, target_file)
        return True

def get_options():
    parser = optparse.OptionParser()
    parser.add_option("-u", "--upgrade", dest="upgrade",
                      help="upgrade folder")
    parser.add_option("-t", "--target", dest="target",
                      help="target folder")
    parser.add_option("-b", "--block", dest="block", default=4*1024, type="int",
                      help="block size")
    parser.add_option("--algorithm", dest="algorithm", default="md5",
                      help="diff algorithm")                      
    parser.add_option("-d", "--diff", dest="diff",
                      help="diff output path")
    parser.add_option("-m", "--map", dest="map",
                      help="map output path")
    parser.add_option("-a", "--apply", dest="apply",
                      help="apply diff to folder")
    (options, args) = parser.parse_args()
    if not (options.apply or options.upgrade or options.target):
        parser.print_help()
        sys.exit(-1)
    return options

if __name__ == "__main__":
    opt = get_options()

    upgrade = BlockMap()
    target = BlockMap()
    apply = BlockMap()

    if opt.block:
        upgrade.set_block_size(opt.block)
        target.set_block_size(opt.block)
        apply.set_block_size(opt.block)

    if opt.algorithm:
        upgrade.set_diff_algorithm(opt.algorithm)
        target.set_diff_algorithm(opt.algorithm)
        apply.set_diff_algorithm(opt.algorithm)

    if opt.diff:
        upgrade.set_diff_path(opt.diff)

    if opt.upgrade:
        upgrade.set_dir_path(opt.upgrade)
        upgrade.get_blocks_map()
        if opt.map:
            upgrade.save_map(opt.map)
    if opt.target:
        target.set_dir_path(opt.target)
        target.get_blocks_map()
        if opt.map:
            target.save_map(opt.map)
    if opt.apply:
        apply.set_dir_path(opt.apply)

    if opt.upgrade and opt.target:
        upgrade.diff_map(target)
        upgrade.create_diff()
    
    if opt.apply:
        upgrade.apply_diff(apply)
