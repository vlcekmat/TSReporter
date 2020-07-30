from tkinter import Tk
from tkinter import filedialog


def find_path():
    # Opens dialogue window and returns the selected directory
    root = Tk()
    root.withdraw()
    dir_path = filedialog.askdirectory()
    return dir_path


def find_image_path():
    # Opens dialogue window and returns the selected jpg or gif
    # If filedialog us closed manually, returns None
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfile(
        filetypes=[
            ("image", ".jpeg"),
            ("image", ".jpg"),
            ("gif", ".gif")
        ]
    )
    if not file_path:
        return None
    else:
        return file_path.name


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


def ask_yes_no():
    while True:
        ans = input("Answer Y/N\n> ")
        if ans.upper() in ["Y", "YES", "YEP", "YEA", "T", "TRUE"]:
            return True
        elif ans.upper() in ["N", "NO", "NOPE", "NAH", "F", "FALSE"]:
            return False
