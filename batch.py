from information_compile import get_image


def check_batch_images(all_bugs):
    # Checks if all reports in bugs.txt have an image, asks user to check again if not
    # returns True if the user wants to stop batch reporting and return to menu, otherwise False
    try_again = True
    while try_again:
        img_missing = False
        for bug in all_bugs:  # Bug is stack of main bug line and all attached .report
            if bug[0][0] not in [';', '!']:
                img = get_image(bug[0])
                if not img:

                    img_missing = True
        if img_missing:

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


def check_batch_formats(bug_lines):
    # Checks every line in bugs.txt and determines if the file is valid and ready to be batch reported
    line_no = 0
    format_is_correct = True
    for line in bug_lines:
        line_no += 1
        if line[0] in ['.', '!', ';']:  # Reports beginning with '.' are added to the previous report
            continue
        # In batch mode, bugs must be prefixed by their priority
        elif '_' in line and line.split('_', maxsplit=1)[0].lower() in ['l', 'n', 'h', 'u', 'i']:
            continue
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
        print('"' + out_prefix + '"')
        answer = input("Is your prefix correct(Y/N)?\n> ")
        if answer.upper() == 'Y':
            return out_prefix
