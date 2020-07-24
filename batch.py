import copy
from collections import deque

from information_compile import get_image


def check_batch_images(all_bugs, image_folder_path):
    # Checks if all reports in bugs.txt have an image, asks user to check again if not
    # returns True if the user wants to stop batch reporting and return to menu, otherwise False
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
    # Checks every line in bugs.txt and determines if the file is valid and ready to be batch reported
    # In doing so, puts all the bugs into deques and adds all those deques into the all_bugs deque
    # That is then used for reporting the bugs
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


def ask_for_prefix():
    # Asks user to provide the prefix that will be added in front of all bug names in the batch report
    while True:
        out_prefix = input("Choose your prefix\n> ")
        if out_prefix == "":
            print("No prefix selected, returning to menu")
            return ""
        print(f"Double check your prefix, you won't be able to change it later!")
        print(out_prefix)
        answer = input("Is your prefix correct(Y/N)?\n> ")
        if answer.upper() == 'Y':
            return out_prefix
