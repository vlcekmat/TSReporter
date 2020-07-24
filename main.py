import os
from collections import deque
import fnmatch

from batch import check_batch_images, check_batch_formats
from bugs import read_bugs_file, archive_bug, read_bug_lines
from utils import ask_use_mode
from reporter import report_bug, batch_report_bugs
import versions as ver
from sector_seek import find_assign_to
from chromedrivers import log_into_tsreporter
from config import ConfigHandler


def main():
    # Program happens here
    password = ""
    cfg_handler = ConfigHandler()

    # Main program loop, ends by selecting mode 4
    while True:
        print('Select desired mode:')
        print('''    1: Report bugs
    2: Batch report (WIP)
    3: Change config
    4: Exit
        ''')

        # Selects a valid use mode and breaks
        use_mode = ask_use_mode()

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

            bug_lines = read_bugs_file(game_path)  # bugs.txt is found and read into bug_lines
            if not bug_lines:  # read_bugs_file() returns none if there is a problem
                continue

            version = ver.find_version(chosen_project[0], cfg_handler)  # Returns -1 if it cant read version
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
                # Here, all bugs in bugs.txt are read and put into a list of stack of individual report lines
                all_bugs = deque()
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


def validate_cfg_images(cfg_handler):
    # Gets edited image location from the config and checks that it exists and has at least one valid file
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
