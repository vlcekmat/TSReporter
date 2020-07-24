import copy
from collections import deque

from information_compile import get_image


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
