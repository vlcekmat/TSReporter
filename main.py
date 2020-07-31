import os
import fnmatch

from batch import check_batch_images, check_batch_formats
from bugs import read_bugs_file, archive_bug, read_bug_lines
from utils import ask_use_mode
from reporter import report_bug, batch_report_bugs
import versions as ver
from sector_seek import find_assign_to
from chromedrivers import log_into_tsreporter
from config import ConfigHandler, validate_cfg_images, read_config


def main():
    # Program happens here
    password = ""
    cfg_handler = ConfigHandler()

    # Main program loop, ends by selecting mode 4
    while True:
        print('Select desired mode:')
        print('''    1: Report bugs
    2: Batch report
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
            report_option(use_mode, password)


def report_option(use_mode, password):
    # This section validates the edited pictures directory from config.cfg
    images_folder = validate_cfg_images()
    if images_folder == "":
        return None

    mantis_username = read_config("mantis username")
    if mantis_username == "":
        print("Mantis username not found in config.cfg")
        return None

    # If password was not entered successfully this session, it happens here
    if password == "":
        password = log_into_tsreporter(mantis_username, read_config("preferred browser"))
        if password == "":
            return None

    doc_path = read_config("documents location")  # Path to documents

    # Here,the user selects which project to report into
    # This is important because it determines which game's files and versions will be accessed
    chosen_project = ver.get_project_from_user()
    if chosen_project[0] == 'A':
        game_path = doc_path + "/American Truck Simulator"
    else:
        game_path = doc_path + "/Euro Truck Simulator 2"

    bug_lines = read_bugs_file(game_path)  # bugs.txt is found and read into bug_lines
    if not bug_lines:  # read_bugs_file() returns none if there is a problem
        return None

    version = ver.find_version(chosen_project[0])  # Returns -1 if it cant read version
    if version == -1:  # Version is not found, would result in invalid report
        return None
    print(f"Reporting in project [{chosen_project}] at version {version}")

    all_bugs = read_bug_lines(bug_lines)

    # Reporting occurs here
    if use_mode == 1:  # Standard reporting use_mode
        while len(all_bugs) > 0:
            current_bug = all_bugs.popleft()
            if current_bug[0][0] not in ['!', ';']:
                assign_to = find_assign_to(current_bug[0], chosen_project[0])
                report_bug(chosen_project, current_bug, version, images_folder, assign_to,
                           mantis_username, password, read_config("preferred browser"))
            archive_bug(current_bug, game_path)

    elif use_mode == 2:  # Batch reporting use_mode
        print("WARNING: Batch reporting is still WIP!")
        # Here, all bugs in bugs.txt are read and put into a list of stack of individual report lines
        format_is_correct = check_batch_formats(bug_lines)
        if not format_is_correct:
            return None

        image_check = check_batch_images(all_bugs)
        if image_check:
            return None

        reported = batch_report_bugs(
            chosen_project, all_bugs, version, images_folder,
            mantis_username, password, read_config("preferred browser")
        )
        if not reported:
            return None
        with open(game_path + "/bugs_archive.txt", "a") as archive:
            archive.writelines(bug_lines)
        with open(game_path + "/bugs.txt", "w"):
            pass
