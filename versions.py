from pathlib import Path
import re
import os

from utils import is_int
from config import read_config


def find_game_version(log_path):
    # Finds the game version from game.log.txt and returns it
    # Uses a Regexp to find the line and then extracts the version
    # Returns -1 if no version is found (eg. when game crashes too soon)
    with open(log_path, "r", encoding='UTF-8') as f:
        f_lines = f.readlines()
    for _line in f_lines:
        ver_line = re.search("00:\d\d:\d\d.\d\d\d : [^0]* Truck Simulator [2\s]*init ver.[\d.]+", _line)
        if ver_line is not None:
            version_0 = _line.split("ver.")[1]
            version_1 = version_0.split(" ")[0]
            return version_1
    return -1


def find_trunk_version(game, trunk_path):
    # Finds the current version of the trunk from the trunk_path
    if game == 'A':
        c_path = Path(trunk_path + "/ATS/CURRENT")
    else:
        c_path = Path(trunk_path + "/ETS2/CURRENT")
    try:
        current = c_path.open(mode='r', encoding='UTF-8')
        trunk_ver = current.read()
        current.close()
    except FileNotFoundError:
        return -1
    ver_out = f"[trunk at revision {trunk_ver[:-1]}]"
    return ver_out


def find_version(game):
    # Takes first letter of game as argument -- A or E for ATS or ETS2
    # Finds the game version in game.log.txt and if it is a trunk version, finds the version in CURRENT
    # returns -1 if game.log.txt is missing or game crashed before printing out game version
    if game == 'A':
        log_path = read_config("documents location") + "/American Truck Simulator/game.log.txt"
    else:
        log_path = read_config("documents location") + "/Euro Truck Simulator 2/game.log.txt"
    if not os.path.isfile(log_path):
        return -1
    found_version = find_game_version(log_path)
    if found_version == -1:
        return -1

    if game == 'A' and found_version == "0.1.3":
        version_out = find_trunk_version(game, read_config("trunk location"))
    elif game == 'E' and found_version == "1.11":
        version_out = find_trunk_version(game, read_config("trunk location"))
    else:
        version_out = "[" + found_version + "]"

    return version_out
