Block Update
===========

[![GitHub license](https://img.shields.io/github/license/peitaosu/Block_Update.svg)](https://github.com/peitaosu/Block_Update/blob/master/LICENSE)

File Update Mechanism based on Block Hash. 

- A mapping file includes folder structure and hash values of file blocks.
- A diff file includes:
    - list of removed files
    - list of added files
    - list of files which have been updated and the hash value difference between upgrade file and target file
- A diff folder includes added files with whole file and updated files with updated file fragments.

Create diff outputs with upgrade folder and target folder and then apply the diff to the folder which you want to update.

## Map
```
{
    "a/b/2": [
        "3ec983b96101f417898364f30f68b0d1"
    ], 
    "a/b/1": [
        "86d647e5b25c2f68ec1e06ef4c506f79"
    ], 
    "c/2": [
        "81dc9bdb52d04dc20036dbd8313ed055"
    ]
}
```

## Diff
```
{
    "removed": [
        "c/3"
    ], 
    "added": [
        "a/b/2"
    ], 
    "updated": {
        "a/b/1": [
            {
                "upgrade": "86d647e5b25c2f68ec1e06ef4c506f79", 
                "target": "6537e99af2c2223642df9f70a0b5afca"
            }
        ], 
        "c/2": [
            {
                "upgrade": "81dc9bdb52d04dc20036dbd8313ed055", 
                "target": "d19e673cb2f4107a51e0253eda41e46c"
            }, 
            {
                "upgrade": "", 
                "target": "cb45cfdc644378338ebe295b4da07c61"
            }, 
            {
                "upgrade": "", 
                "target": "aeab9d7a8d0a119d37bd868b62dfe861"
            }
        ]
    }, 
    "block": 4096,
    "algorithm": "sha256"
}
```

## Usage (Command Line)
```
> python map.py -h

Usage: map.py [options]

Options:
  -h, --help            show this help message and exit
  -u UPGRADE, --upgrade=UPGRADE
                        upgrade folder
  -t TARGET, --target=TARGET
                        target folder
  -b BLOCK, --block=BLOCK
                        block size
  --algorithm=ALGORITHM
                        diff algorithm
  -d DIFF, --diff=DIFF  diff output path
  -m MAP, --map=MAP     map output path
  -a APPLY, --apply=APPLY
                        apply diff to folder

# create map
> python map.py -u upgrade -m upgrade.json [-b 1024] [--algorithm sha256]

# create diff
> python map.py -u upgrade -t target -d diff [-b 1024] [--algorithm sha256]

# apply diff
> python map.py -a apply [-b 1024] [--algorithm sha256]
```

## Usage (Module)
```
from map import *

upgrade = BlockMap()
target = BlockMap()
apply = BlockMap()

# set block size
block = 1024
upgrade.set_block_size(block)
target.set_block_size(block)
apply.set_block_size(block)

# set diff algorithm
algorithm = "sha256"
upgrade.set_diff_algorithm(algorithm)
target.set_diff_algorithm(algorithm)
apply.set_diff_algorithm(algorithm)

# set diff output path
diff_path = "diff"
upgrade.set_diff_path(diff_path)

# get map of upgrade
upgrade_path = "upgrade"
upgrade.set_dir_path(upgrade_path)
upgrade.get_blocks_map()

# save map to file
map_path = "upgrade.json"
upgrade.save_map(map_path)

# get map of target
target_path = "target.json"
target.set_dir_path(target_path)
target.get_blocks_map()

# save map to file
map_path = "target.json"
target.save_map(map_path)

# set apply path
apply_path = "apply"
apply.set_dir_path(apply_path)

# create diff between upgrade and target
upgrade.diff_map(target)
upgrade.create_diff()

# apply diff
upgrade.apply_diff(apply)
```
