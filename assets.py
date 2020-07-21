import os
import re


def get_asset_name(game):
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

    f = open(log_path, "r")
    for _line in f:
        ver_line = re.search("00:\d\d:\d\d.\d\d\d : DEBUG INFO:", _line)
        if ver_line is not None:
            version_0 = _line.split("ver.")[1]
            version_1 = version_0.split(" ")[0]
            return version_1
