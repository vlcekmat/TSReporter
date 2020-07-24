from tkinter import Tk
from tkinter import filedialog


def find_path():
    # Opens dialogue window and returns the selected directory
    root = Tk()
    root.withdraw()
    dir_path = filedialog.askdirectory()
    return dir_path


def is_int(s):
    # Tests if string is a valid int
    try:
        int(s)
        return True
    except TypeError:
        return False
    except ValueError:
        return False


def ask_use_mode():
    while True:
        use_mode = input('> ')
        if not is_int(use_mode):
            continue
        if 1 <= int(use_mode) <= 4:
            return int(use_mode)


# def ask_yes_no():
#     while True:
#         ans = input("Answer Y/N\n> ")
#         if ans.upper() in ["Y", "YES", "YEP", "YEA"]:
#             return True
#         elif ans.upper() in ["N", "NO", "NOPE", "NAH"]:
#             return False
