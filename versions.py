from pathlib import Path
import re
import os

from utils import is_int


# Asks user which project they want their reports will go into and returns project name as string
# All bugs will be reported into that project
def get_project_from_user():
    projects = ['ATS - INTERNAL', 'ATS - PUBLIC', 'ATS - PUBLIC - SENIORS', 'ETS 2 - INTERNAL', 'ETS 2 - PUBLIC',
                'ETS 2 - PUBLIC - SENIORS']
    print('Choose a project')
    for i in range(len(projects)):
        print(f"{i + 1}: {projects[i]}")
    while True:
        project = input('> ')
        if not (is_int(project) and 6 >= int(project) >= 1):
            print('Invalid project, choose a number between 1 and 6')
            continue
        else:
            return projects[int(project) - 1]


# Finds the game version from game.log.txt and returns it
# Uses a Regexp to find the line and then extracts the version
# Returns -1 if no version is found (eg. when game crashes too soon)
def find_game_version(log_path):
    f = open(log_path, "r")
    for _line in f:
        ver_line = re.search("00:\d\d:\d\d.\d\d\d : [^0]* Truck Simulator [2\s]*init ver.[\d.]+", _line)
        if ver_line is not None:
            version_0 = _line.split("ver.")[1]
            version_1 = version_0.split(" ")[0]
            return version_1
    print("Game version not found in game log!")
    return -1


# Finds the current version of the trunk from the trunk_path
def find_trunk_version(game, trunk_path):
    if game == 'A':
        c_path = Path(trunk_path + "/ATS/CURRENT")
    else:
        c_path = Path(trunk_path + "/ETS2/CURRENT")
    try:
        current = c_path.open(mode='r', encoding='utf-8')
        trunk_ver = current.read()
        current.close()
    except FileNotFoundError:
        print(f"CURRENT not found in file: {c_path}")
        return -1
    ver_out = f"[trunk at revision {trunk_ver[:-1]}]"
    return ver_out


# Takes first letter of game as argument -- A or E for ATS or ETS2
# Finds the game version in game.log.txt and if it is a trunk version, finds the version in CURRENT
# returns -1 if game.log.txt is missing or game crashed before printing out game version
def find_version(game):
    _cfg_file = open("./config.cfg", "r")
    _doc_read = _cfg_file.readlines()
    _cfg_file.close()
    if game == 'A':
        log_path = _doc_read[1][:-1] + "/American Truck Simulator/game.log.txt"
    else:
        log_path = _doc_read[1][:-1] + "/Euro Truck Simulator 2/game.log.txt"
    if not os.path.isfile(log_path):
        print(f"game.log.txt not found in path {log_path}")
        return -1
    found_version = find_game_version(log_path)
    if found_version == -1:
        return -1

    if game == 'A' and found_version == "0.1.3":
        version_out = find_trunk_version(game, _doc_read[0][:-1])
    elif game == 'E' and found_version == "1.11":
        version_out = find_trunk_version(game, _doc_read[0][:-1])
    else:
        version_out = "[" + found_version + "]"

    return version_out
