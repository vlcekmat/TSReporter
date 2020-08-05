import fnmatch

from utils import is_int, find_path, ask_yes_no
import os
from ast import literal_eval
from sys import stdout


def read_config(key):
    return ConfigHandler.cfg_dict[key]


def write_config(key, value):
    try:
        ConfigHandler.cfg_dict[key] = value
        ConfigHandler.save_config()
        return True
    except KeyError:
        return False


class ConfigHandler:
    cfg_dict = {}

    # This is the layout of the config.cfg file by lines. Use this to inform the user or validate config.cfg
    # If a new config option needs to be added, add it here and validate_config() will ask it from user
    config_layout = {
            "trunk location": "path",
            "documents location": "path",
            "edited images location": "path",
            "mantis username": "text",
            "preferred browser": "browser",
            "save password": "yn",
            "s_password": "secret"
    }

    def __init__(self, debug=False):
        if debug:
            config_path = "tests/config.cfg"
        else:
            config_path = "./config.cfg"
        if not os.path.isfile(config_path):
            ConfigHandler.gui_config_setup()  # changed from config_setup()
        else:
            cfg_file = open(config_path, "r")
            cfg_lines = cfg_file.readlines()
            for i in enumerate(cfg_lines):
                cfg_lines[i[0]] = cfg_lines[i[0]][:-1]
            temp_dict = "{" + ", ".join(cfg_lines) + "}"
            ConfigHandler.cfg_dict = literal_eval(temp_dict)
            ConfigHandler.validate_config()

    @staticmethod
    def validate_config():
        # Looks at the config_layout and checks if any lines are missing. If so, asks for them and saves to config
        config_layout = ConfigHandler.config_layout
        config_wasnt_valid = False
        for layout_item in config_layout.keys():
            if layout_item not in ConfigHandler.cfg_dict.keys():
                if config_layout[layout_item] == "secret":
                    ConfigHandler.cfg_dict[layout_item] = ""
                    config_wasnt_valid = True
                    continue
                print("Your config.cfg is missing some lines!")
                ConfigHandler.cfg_dict[layout_item] = ConfigHandler.ask_config_line(layout_item)
                config_wasnt_valid = True
        if ConfigHandler.cfg_dict["save password"] == "False":
            if ConfigHandler.cfg_dict["s_password"] != "":
                config_wasnt_valid = True
                ConfigHandler.cfg_dict["s_password"] = ""
        if config_wasnt_valid:
            ConfigHandler.save_config()

    @staticmethod
    def list_config():
        # Lists contents of config.cfg
        i = 1
        for key in ConfigHandler.cfg_dict:
            if ConfigHandler.config_layout[key] != "secret":
                print(str(i) + ": " + key + ":\t\t" + str(ConfigHandler.cfg_dict[key]))
                i += 1

    @staticmethod
    def save_config(o_stream=None):
        # Saves content of dictionary to config.cfg in correct format
        cfg_file = open("./config.cfg", "w")
        for key in ConfigHandler.cfg_dict:
            cfg_file.write(f'"{key}" : "{ConfigHandler.cfg_dict[key]}"\n')
        if o_stream:
            pass
            # o_stream.write("Configuration changes saved")

    @staticmethod
    def config_edit():
        # Shows contents of config.cfg to the user and gives them the option to edit any of the configurations
        cfg_dict = ConfigHandler.config_layout

        cfg_layout = []
        for key in cfg_dict.keys():
            cfg_layout.append(key)

        while True:
            print("These is your current configuration, type the number of what you want to modify:")
            print("0: Exit config")
            ConfigHandler.list_config()
            line_selection = input("> ")

            if not is_int(line_selection) or not 0 <= int(line_selection) <= len(cfg_layout):
                print("Invalid choice")
                continue
            else:
                ls = int(line_selection)

            if ls == 0:
                break
            else:
                ls -= 1
                ConfigHandler.cfg_dict[cfg_layout[ls]] = ConfigHandler.ask_config_line(cfg_layout[ls])
                ConfigHandler.save_config(stdout)
                continue
        if read_config("save password") == "False":
            write_config("s_password", "")

    @staticmethod
    def gui_config_edit(index, entered_text=None, yes_no_value=None, browser_chosen=None):
        cfg_layout = []
        for key in ConfigHandler.config_layout.keys():
            if ConfigHandler.config_layout[key] != "secret":
                cfg_layout.append(key)

        line_selection = index
        if entered_text is not None:
            ConfigHandler.cfg_dict[cfg_layout[line_selection]] = ConfigHandler.ask_config_line(
                cfg_layout[line_selection]
                , entered_text=entered_text)
        elif yes_no_value is not None:
            ConfigHandler.cfg_dict[cfg_layout[line_selection]] = ConfigHandler.ask_config_line(
                cfg_layout[line_selection]
                , yes_no_value=yes_no_value)
        elif browser_chosen is not None:
            ConfigHandler.cfg_dict[cfg_layout[line_selection]] = ConfigHandler.ask_config_line(
                cfg_layout[line_selection]
                , preferred_browser=browser_chosen)
        else:
            ConfigHandler.cfg_dict[cfg_layout[line_selection]] = ConfigHandler.ask_config_line(
                cfg_layout[line_selection])
        ConfigHandler.save_config()

    @staticmethod
    def config_setup():
        # Opens windows dialogue windows and has the user select their Trunk, Steam and edited pictures directories
        # Then reads Mantis username from user input
        # Saves the directories to './config.cfg'
        print("No config.cfg file detected, running first time setup")
        cfg_layout = ConfigHandler.config_layout.keys()
        for entry in cfg_layout:
            if ConfigHandler.config_layout[entry] == "secret":
                continue
            ConfigHandler.cfg_dict[entry] = ConfigHandler.ask_config_line(entry)
        ConfigHandler.save_config(stdout)

    @staticmethod
    def gui_config_setup():
        cfg_layout = ConfigHandler.config_layout.keys()
        for entry in cfg_layout:
            if ConfigHandler.config_layout[entry] == "secret":
                ConfigHandler.cfg_dict[entry] = ""
            elif ConfigHandler.config_layout[entry] == "path":
                ConfigHandler.cfg_dict[entry] = "ENTER A PATH"
            elif ConfigHandler.config_layout[entry] == "text":
                ConfigHandler.cfg_dict[entry] = ""
            elif ConfigHandler.config_layout[entry] == "browser":
                ConfigHandler.cfg_dict[entry] = "chrome"
            elif ConfigHandler.config_layout[entry] == "yn":
                ConfigHandler.cfg_dict[entry] = False

        ConfigHandler.save_config(stdout)

    @staticmethod
    def ask_config_line(key_to_ask, entered_text=None, yes_no_value=None, preferred_browser=None):
        # Asks user to select new configuration item based on the contents of the received token
        cfg_type = ConfigHandler.config_layout[key_to_ask]
        if cfg_type == "yn":
            #print(f"Would you like to {key_to_ask}")
            new_value = yes_no_value
        else:
            if cfg_type != "text":
                #print(f"Select your {key_to_ask}")
                pass
            new_value = ""
            if cfg_type == "path":
                new_value = find_path()
            elif cfg_type == "browser":
                new_value = preferred_browser
            elif cfg_type == "text":
                new_value = entered_text

        return new_value


def ask_preferred_browser():
    # Asks user for preferred browser
    while True:
        pref_browser = input("Do you want to use Chrome, Firefox (or Edge)? Type C/F/E\n> ")
        if pref_browser.upper() == 'C':
            return 'chrome'
        elif pref_browser.upper() == 'F':
            return 'firefox'
        elif pref_browser.upper() == 'E':
            print("Visit:")
            print("\thttps://www.google.com/chrome/")
            print("\thttps://www.mozilla.org/en-US/firefox/new/")


def validate_cfg_images():
    # Gets edited image location from the config and checks that it exists and has at least one valid file
    images_folder = read_config("edited images location")
    if images_folder == "":
        print("Edited images folder missing from config.cfg. Set it up before reporting.")
        return ""
    for is_this_image in os.listdir(images_folder):
        if fnmatch.fnmatch(is_this_image, "*.jpg") or fnmatch.fnmatch(is_this_image, "*.gif"):
            return images_folder
    else:
        print("Edited pictures folder doesn't contain any .jpg or .gif files. Did you select the right one?")
        return ""
