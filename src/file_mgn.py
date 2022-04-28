import os

def listAllFiles(dir_path):
    return [os.path.abspath(os.path.join(dir_path, f)) for f in os.listdir(dir_path)]
