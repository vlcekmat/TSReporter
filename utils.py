from tkinter import Tk
from tkinter import filedialog
import re


def find_path():
    # Opens dialogue window and returns the selected directory
    root = Tk()
    root.withdraw()
    dir_path = filedialog.askdirectory()
    return dir_path


def is_hex_color(h):
    match = re.search(r'^#([0-9a-fA-F]{6})$', h)
    if match:
        return True
    else:
        return False


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

# theme_dict = {
#         "ph": {
#             # Change the values below to change the overall color theme of the app
#             1: 'white',  # Regular Buttons
#             2: '#ffa500',  # Quit Button, text
#             3: '#484848',  # Integrated Frames
#             4: '#2B2B2B'  # Background
#         },
#
#         "campfire": {
#             # Change the values below to change the overall color theme of the app
#             1: '#03A678',  # Regular Buttons
#             2: '#F28C0F',  # Quit Button, text
#             3: '#02735E',  # Integrated Frames
#             4: '#014040'  # Background
#         },
#
#         "hazard_theme": {
#             # Change the values below to change the overall color theme of the app
#             1: '#BD554A',  # Regular Buttons
#             2: '#CF423C',  # Quit Button, text
#             3: '#570B2A',  # Integrated Frames
#             4: '#33081E'  # Background
#         },
#
#         "candle": {
#             # Change the values below to change the overall color theme of the app
#             1: '#6EAFB5',  # Regular Buttons
#             2: '#FD9F75',  # Quit Button, text
#             3: '#185572',  # Integrated Frames
#             4: '#05395E'  # Background
#         },
#
#         "navy": {
#             # Change the values below to change the overall color theme of the app
#             1: '#387097',  # Regular Buttons
#             2: 'white',  # Quit Button, text
#             3: '#1F384C',  # Integrated Frames
#             4: '#1B2838'  # Background
#         },
#
#         "purple_rain": {
#             # Change the values below to change the overall color theme of the app
#             1: '#ECE8E1',  # Regular Buttons
#             2: '#FF4655',  # Quit Button, text
#             3: '#8C3243',  # Integrated Frames
#             4: '#271D26'  # Background
#         },
#
#         "storm": {
#             # Change the values below to change the overall color theme of the app
#             1: '#908CAC',  # Regular Buttons
#             2: '#C3BBD2',  # Quit Button, text
#             3: '#3F384F',  # Integrated Frames
#             4: '#1A1E26'  # Background
#         },
#
#         "grayscale": {
#             # Change the values below to change the overall color theme of the app
#             1: '#838383',  # Regular Buttons
#             2: '#D9D9D9',  # Quit Button, text
#             3: '#404040',  # Integrated Frames
#             4: '#262626'  # Background
#         }
#     }
