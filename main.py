import os
from collections import deque
import fnmatch
import copy

from batch import check_batch_images, check_batch_formats
from utils import is_int
from reporter import report_bug, batch_report_bugs
import versions as ver
from sector_seek import find_assign_to
from chromedrivers import log_into_tsreporter
from config import ConfigHandler


# Program happens here
def main():
    password = "CrYVhn7FSM"
    cfg_handler = ConfigHandler()

    # Main program loop, ends by selecting mode 3
    while True:
        print('Select desired mode:')
        print('''    1: Report bugs
    2: Batch report (WIP)
    3: Change config
    4: Exit
        ''')

        # Selects a valid use mode and breaks
        while True:
            use_mode = input('> ')
            if not is_int(use_mode):
                continue
            if 1 <= int(use_mode) <= 4:
                use_mode = int(use_mode)
                break

        # noinspection PyUnboundLocalVariable
        if use_mode == 4:  # Quit use_mode
            print("Ending")
            break

        elif use_mode == 3:  # Edit configuration use_mode
            cfg_handler.config_edit()

        elif use_mode in [1, 2]:  # Report bugs use_mode

            # This section validates the edited pictures directory from config.cfg
            images_folder = validate_cfg_images(cfg_handler)
            if images_folder == "":
                continue

            mantis_username = cfg_handler.read("mantis username")
            if mantis_username == "":
                print("Mantis username not found in config.cfg")
                continue

            # If password was not entered successfully this session, it happens here
            if password == "":
                password = log_into_tsreporter(mantis_username, cfg_handler.read("preferred browser"))
                if password == "":
                    continue

            doc_path = cfg_handler.read("documents location")  # Path to documents

            # Here,the user selects which project to report into
            # This is important because it determines which game's files and versions will be accessed
            chosen_project = ver.get_project_from_user()
            if chosen_project[0] == 'A':
                game_path = doc_path + "/American Truck Simulator"
            else:
                game_path = doc_path + "/Euro Truck Simulator 2"

            # bugs.txt is found and read into bug_lines
            bug_lines = read_bugs_file(game_path)
            if not bug_lines:
                continue

            version = ver.find_version(chosen_project[0], cfg_handler)
            if version == -1:  # Version is not found, would result in invalid report
                continue
            print(f"Reporting in project [{chosen_project}] at version {version}")

            # Reporting occurs here
            if use_mode == 1:  # Standard reporting use_mode
                all_bugs = read_bug_lines(bug_lines)
                while len(all_bugs) > 0:
                    current_bug = all_bugs.popleft()
                    if current_bug[0][0] not in ['!', ';']:
                        assign_to = find_assign_to(current_bug[0], chosen_project[0])
                        report_bug(chosen_project, current_bug, version, images_folder, assign_to,
                                   mantis_username, password, cfg_handler.read("preferred browser"))
                    archive_bug(current_bug, game_path)

            elif use_mode == 2:  # Batch reporting use_mode
                print("WARNING: Batch reporting is still WIP!")
                # This prefix will be added at the beginning of all summaries to save time
                # eg. writing "State - City -" at the beginning of each report
                all_bugs = deque()

                # Here, all bugs in bugs.txt are read and put into a list of stack of individual report lines
                format_is_correct = check_batch_formats(bug_lines, all_bugs)
                if not format_is_correct:
                    continue

                image_check = check_batch_images(all_bugs, images_folder)
                if image_check:
                    continue

                reported_all = batch_report_bugs(
                    chosen_project, all_bugs, version, images_folder,
                    mantis_username, password, cfg_handler.read("preferred browser")
                     )
                if not reported_all:
                    continue
                # TODO: Add archiving


def read_bugs_file(game_path):
    if not os.path.isfile(game_path + "/bugs.txt"):
        print(f"bugs.txt not found in {game_path}. Change config or report some bugs first.")
        return None

    bugs_file = open(game_path + "/bugs.txt", "r")
    bug_lines = bugs_file.readlines()
    bugs_file.close()

    while '\n' in bug_lines:  # Cleanses bug_lines of empty lines to prevent later crash
        bug_lines.remove('\n')

    if bug_lines[0][0] == '.':  # If first line starts with a '.', everything will break, don't even think about it
        print("First report's name begins with a '.', go fix that!")
        return None
    if len(bug_lines) == 0:  # Why bother reporting huh
        print("No bugs to report from bugs.txt")
        return None

    return bug_lines


def archive_bug(current_bug, game_path):
    bugs_location = game_path + "/bugs.txt"
    with open(game_path + "/bugs_archive.txt", "a") as archive:
        while len(current_bug) > 0:
            line_to_archive = current_bug.popleft()
            archive.write(line_to_archive)
            with open(bugs_location, 'r') as bugs_file:
                bugs_source = bugs_file.read()
                bugs_removed = bugs_source.replace(line_to_archive, '')
            with open(bugs_location, 'w') as bugs_file:
                bugs_file.write(bugs_removed)


# Processes bug_lines and divides them up into sub-deques in the all_bugs deque
# Popping from all_bugs will give you a deque that contains a bug head and all its extra image lines
# Lines that are meant to be ignored are still added to all_bugs and must be archived and cleansed later
def read_bug_lines(bug_lines):
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


def validate_cfg_images(cfg_handler):
    images_folder = cfg_handler.read("edited images location")
    if images_folder == "":
        print("Edited images folder missing from config.cfg. Set it up before reporting.")
        return ""
    for is_this_image in os.listdir(images_folder):
        if fnmatch.fnmatch(is_this_image, "*.jpg") or fnmatch.fnmatch(is_this_image, "*.gif"):
            return images_folder
    else:
        print("Edited pictures folder doesn't contain any .jpg or .gif files. Did you select the right one?")
        return ""


# Program begins here
print("Welcome to TSReporter")
main()
