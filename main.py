import os
from collections import deque
import fnmatch
import copy

from utils import is_int
from reporter import report_bug, batch_report_bugs
import versions as ver
from sector_seek import find_assign_to
from chromedrivers import log_into_tsreporter
from config import ConfigHandler
from information_compile import get_image


# Program happens here
def main():
    password = ""
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
            images_folder = cfg_handler.read("edited images location")
            if images_folder == "":
                print("Edited images folder missing from config.cfg. Set it up before reporting.")
                continue
            for is_this_image in os.listdir(images_folder):
                if fnmatch.fnmatch(is_this_image, "*.jpg") or fnmatch.fnmatch(is_this_image, "*.gif"):
                    break
            else:
                print("Edited pictures folder doesn't contain any .jpg or .gif files. Did you select the right one?")
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
            if not os.path.isfile(game_path + "/bugs.txt"):
                print(f"bugs.txt not found in {game_path}. Change config or report some bugs first.")
                continue
            bugs_file = open(game_path + "/bugs.txt", "r")
            bug_lines = bugs_file.readlines()
            bugs_file.close()
            if len(bug_lines) == 0:
                print("No bugs to report from bugs.txt")
                continue

            version = ver.find_version(chosen_project[0], cfg_handler)
            if version == -1:  # Version is not found, would result in invalid report
                continue
            print(f"Reporting in project [{chosen_project}] at version {version}")

            while '\n' in bug_lines:  # Cleanses bug_lines of empty lines to prevent later crash
                bug_lines.remove('\n')

            archive = open(game_path + "/bugs_archive.txt", "a")

            # Reporting occurs here
            if use_mode == 1:  # Standard reporting use_mode
                lines_to_report = deque()  # Implemented as a stack
                lines_to_archive = deque()
                try:
                    for line in reversed(bug_lines):
                        archive.write(line)
                        if line[0] == '.':  # Reports beginning with '.' are added to the previous report
                            lines_to_report.append(line)
                            continue
                        elif line[0] == '!' or line[0] == ';':  # Reports beginning with '!' or blank ones are ignored
                            continue
                        else:
                            lines_to_report.append(line)

                        assign_to = find_assign_to(line, chosen_project[0])

                        report_bug(chosen_project, lines_to_report, version, images_folder, assign_to,
                                   mantis_username, password, cfg_handler.read("preferred browser"))
                        lines_to_report.clear()
                        print("Bug reported successfully!\n")
                finally:
                    # All bugs that were reported during one reporting cycle will now be added to archive
                    archive = open(game_path + "/bugs_archive.txt", "a")
                    while len(lines_to_archive) > 0:
                        archive_me = lines_to_archive.pop()
                        archive.write(archive_me)
                    archive.close()
                    # Clear bugs.txt after use, all have been saved to archive
                    bugs_file = open(game_path + "/bugs.txt", "w")
                    bugs_file.close()

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


# Checks if all reports in bugs.txt have an image, asks user to check again if not
# returns True if the user wants to stop batch reporting and return to menu, otherwise False
def check_batch_images(all_bugs, image_folder_path):
    try_again = True
    img_missing = False
    while try_again:
        for bug in all_bugs:  # Bug is stack of main bug line and all attached .report
            img = get_image(bug[0], image_folder_path)
            if not img:
                print(f"Image not found for bug: {bug[0][:-1]}")
                img_missing = True
        if img_missing:
            print("Would you like to try again or quit to menu? ")
            while True:
                ans = input("Y/N/Q\n> ")
                if ans.upper() == "Y":
                    try_again = True
                    break
                elif ans.upper() == "N":
                    try_again = False
                    break
                elif ans.upper() == "Q":
                    return True
        else:
            try_again = False
    return False


def check_batch_formats(bug_lines, all_bugs):
    line_no = len(bug_lines) + 1
    temp_bug_deque = deque()
    format_is_correct = True
    for line in reversed(bug_lines):
        line_no -= 1
        if line[0] == '.':  # Reports beginning with '.' are added to the previous report
            temp_bug_deque.append(line)
            continue
        elif line[0] == '!' or line[0] == ';':  # Reports beginning with '!' or blank ones are ignored
            continue
        # In batch mode, bugs must be prefixed by their priority
        elif '_' in line and line.split('_', maxsplit=1)[0].lower() in ['l', 'n', 'h', 'u', 'i']:
            temp_bug_deque.append(line)
            all_bugs.append(copy.deepcopy(temp_bug_deque))
            temp_bug_deque.clear()
        else:
            print(f"Invalid format of bug on line {line_no}:\n{line}")
            format_is_correct = False
            continue
    return format_is_correct


# Program begins here
print("Welcome to TSReporter")
main()
