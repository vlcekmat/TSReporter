import copy
import os
from collections import deque

import config


def read_bugs_file(game_path, o_stream):
    # Reads bugs.txt, validates it and returns the read lines
    if not os.path.isfile(game_path + "/bugs.txt"):
        o_stream.write(
            f"bugs.txt not found in {game_path}. Change config or report some bugs first.\n")
        return None

    bugs_file = open(game_path + "/bugs.txt", "r", encoding='UTF-8')
    bug_lines = bugs_file.readlines()
    bugs_file.close()

    while '\n' in bug_lines:  # Cleanses bug_lines of empty lines to prevent later crash
        bug_lines.remove('\n')

    if len(bug_lines) == 0:  # Why bother reporting huh
        o_stream.write("No bugs to report from bugs.txt\n")
        return None
    if bug_lines[0][0] == '.':  # If first line starts with a '.', everything will break, don't even think about it
        o_stream.write("First report's name begins with a '.', go fix that!\n")
        return None

    return bug_lines


def archive_bug(current_bug, game_path):
    # Writes the bug deque line by line into archive and removes and removes lines from bugs.txt
    bugs_location = game_path + "/bugs.txt"
    with open(game_path + "/bugs_archive.txt", "a", encoding='UTF-8') as archive:
        while len(current_bug) > 0:
            line_to_archive = current_bug.popleft()
            archive.write(line_to_archive)
            with open(bugs_location, 'r', encoding='UTF-8') as bugs_file:
                bugs_source = bugs_file.read()
                bugs_removed = bugs_source.replace(line_to_archive, '')
            with open(bugs_location, 'w', encoding='UTF-8') as bugs_file:
                bugs_file.write(bugs_removed)


def read_bug_lines(bug_lines):
    # Processes bug_lines and divides them up into sub-deques in the all_bugs deque
    # Popping from all_bugs will give you a deque that contains a bug head and all its extra image lines
    # Lines that are meant to be ignored are still added to all_bugs and must be archived and cleansed later
    all_bugs = deque()
    this_bug = deque()

    this_bug.append(bug_lines[0])
    if len(bug_lines) > 1:
        for line in bug_lines[1:]:
            if line[0] in [';', '!']:  # Ignored lines are added as separate bugs, remove and archive before reporting!
                temp_deque = deque()
                temp_deque.append(line)
                all_bugs.append(temp_deque)
                continue
            elif line[0] == '.':
                this_bug.append(line)
            else:  # All others are valid bug heads
                all_bugs.append(copy.deepcopy(this_bug))   # Return the previous bug
                this_bug.clear()            # and start a new one
                this_bug.append(line)
    all_bugs.append(this_bug)  # The last bug must also be added!
    return all_bugs


def count_bugs():
    ets_bugs_count = 0
    ats_bugs_count = 0
    cfg_handler = config.ConfigHandler()
    documents_location = config.read_config('documents location')
    ats_bugs_path = f"{documents_location}/American Truck Simulator/bugs.txt"
    ets_bugs_path = f"{documents_location}/Euro Truck Simulator 2/bugs.txt"
    ats_bugs = open(ats_bugs_path, encoding='UTF-8')
    ets_bugs = open(ets_bugs_path, encoding='UTF-8')

    for line in ats_bugs:
        if ';' in line and line[0] not in ['!', ';', '.']:
            ats_bugs_count += 1
    for line in ets_bugs:
        if ';' in line and line[0] not in ['!', ';', '.']:
            ets_bugs_count += 1
    return [ats_bugs_count, ets_bugs_count]