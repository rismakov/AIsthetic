import os

def get_filesnames_in_dir(dir):
    return [
        name for name in os.listdir(dir) 
        if os.path.isfile(os.path.join(dir, name)) and name != '.DS_Store'
    ]