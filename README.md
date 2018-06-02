Block Update
===========

File Update Mechanism based on Block Hash. 

## Usage
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
  -d DIFF, --diff=DIFF  diff output path
  -m MAP, --map=MAP     map output path
  -a APPLY, --apply=APPLY
                        apply diff to folder

# create map
> python map.py -u upgrade -m upgrade.json

# create diff
> python map.py -u upgrade -t target -b 1024 -d diff

# apply diff
> python map.py -a apply -b 1024 
```
