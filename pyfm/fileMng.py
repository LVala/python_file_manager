from datetime import datetime, timezone
import shutil
import os
import stat

def listAllFiles(dirPath):
    return [os.path.abspath(os.path.join(dirPath, f)) for f in os.listdir(dirPath)]

def moveAllFiles(paths, dest):
    for path in paths:
        shutil.move(path, dest)

def copyAllFiles(paths, dest):
    for path in paths:
        shutil.copy(path, dest) 

def removeAllFiles(paths):
    for path in paths:
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)

def createDirectory(path):
    os.makedirs(path)  # TODO rzuca wyjątek jeśli już istnieje

def createEmptyFile(path):
    open(path, 'a').close()

def getFileInfo(path):
    fileStat = os.stat(path)
   
    stat_dir = {}
    if stat.S_ISDIR(fileStat[stat.ST_MODE]):
        stat_dir["type"] = "Directory"
    elif stat.S_ISCHR(fileStat[stat.ST_MODE]):
        stat_dir["type"] = "Character special device"
    elif stat.S_ISBLK(fileStat[stat.ST_MODE]):
        stat_dir["type"] = "Block special device"
    elif stat.S_ISREG(fileStat[stat.ST_MODE]):
        stat_dir["type"] = "Regular File"
    elif stat.S_ISFIFO(fileStat[stat.ST_MODE]):
        stat_dir["type"] = "FIFO"
    elif stat.S_ISLNK(fileStat[stat.ST_MODE]):
        stat_dir["type"] = "Symbolic link"
    elif stat.S_ISSOCK(fileStat[stat.ST_MODE]):
        stat_dir["type"] = "Socket"

    stat_dir["permissions"] = stat.filemode(fileStat[stat.ST_MODE])
    stat_dir["size"] = fileStat[stat.ST_SIZE]
    stat_dir["lastmod"] = fileStat[stat.ST_MTIME]
    stat_dir["lastmod"] = datetime.fromtimestamp(stat_dir["lastmod"], tz=timezone.utc)
    stat_dir["lastaccess"] = fileStat[stat.ST_ATIME]
    stat_dir["lastaccess"] = datetime.fromtimestamp(stat_dir["lastaccess"], tz=timezone.utc)
    stat_dir["lastmeta"] = fileStat[stat.ST_CTIME]
    stat_dir["lastmeta"] = datetime.fromtimestamp(stat_dir["lastmeta"], tz=timezone.utc)

    return stat_dir

def changeUnit(value):
    if value < 2**10:
        return value, "B"
    elif value <2**20:
        return value / 2**10, "KiB"
    elif value <2**30:
        return value / 2**20, "MiB"
    else:
        return value / 2**30, "GiB"

def getPartUsage(path):
    total, _, free = shutil.disk_usage(path)
    return changeUnit(total), changeUnit(free)

def renameFile(path, newname):
    os.rename(path, newname)