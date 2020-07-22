import os
from collections import deque
import fnmatch

from utils import is_int
from reporter import report_bug
import versions as ver
from sector_seek import find_assign_to
from chromedrivers import log_into_tsreporter
from config import ConfigHandler


# Program happens here
def main():
    password = ""
    cfg_handler = ConfigHandler()

    # Main program loop, ends by selecting mode 3
    while True:
        print('Select desired mode:')
        print('''    1: Report bugs
    2: Change config
    3: Exit
        ''')

        # Selects a valid use mode and breaks
        while True:
            use_mode = input('> ')
            if not is_int(use_mode):
                continue
            if 1 <= int(use_mode) <= 3:
                use_mode = int(use_mode)
                break

        # noinspection PyUnboundLocalVariable
        if use_mode == 3:  # Quit use_mode
            print("Ending")
            break
        elif use_mode == 2:  # Edit configuration use_mode
            cfg_handler.config_edit()
        elif use_mode == 1:  # Report bugs use_mode

            # This section validates the edited pictures directory from config.cfg
            pictures_folder = cfg_handler.read("edited images location")
            if pictures_folder == "":
                print("Edited pictures folder missing from config.cfg. Set it up before reporting.")
                continue
            for is_this_image in os.listdir(pictures_folder):
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

            # Reporting occurs here
            lines_to_report = deque()  # Implemented as a stack
            lines_to_archive = deque()
            try:
                for line in reversed(bug_lines):
                    lines_to_archive.append(line)  # These will be added to archive in finally: block
                    if line[0] == '.':  # Reports beginning with '.' are added to the previous report
                        lines_to_report.append(line)
                        continue
                    elif line[0] == '!' or line[0] == ';':  # Reports beginning with '!' or blank ones are ignored
                        continue
                    else:
                        lines_to_report.append(line)

                    assign_to = find_assign_to(line, chosen_project[0])

                    report_bug(chosen_project, lines_to_report, version, pictures_folder, assign_to,
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

            bugs_file = open(game_path + "/bugs.txt", "w")  # Clear bugs.txt after use, all have been saved to archive
            bugs_file.close()


# The program begins here
print('Welcome to TSReporter!')
main()
