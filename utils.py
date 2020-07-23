from tkinter import Tk
from tkinter import filedialog


# Opens dialogue window and returns the selected directory
def find_path():
    root = Tk()
    root.withdraw()
    dir_path = filedialog.askdirectory()
    return dir_path


# Tests if string is a valid int
def is_int(s):
    try:
        int(s)
        return True
    except TypeError:
        return False
    except ValueError:
        return False


# def ask_yes_no():
#     while True:
#         ans = input("Answer Y/N\n> ")
#         if ans.upper() in ["Y", "YES", "YEP", "YEA"]:
#             return True
#         elif ans.upper() in ["N", "NO", "NOPE", "NAH"]:
#             return False
