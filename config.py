import fnmatch
from ast import literal_eval

from utils import is_int, find_path
import os


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
    # If a new config option needs to be added, add it here
    config_layout = {
            "trunk location": "path",
            "documents location": "path",
            "edited images location": "path",
            "mantis username": "text",
            "preferred browser": "browser",
            "save password": "yn",
            "s_password": "secret",
            "current_theme": "secret",
            # "renamed images location": "path"
    }

    def __init__(self, debug=False):
        if debug:
            config_path = "tests/config.cfg"
        else:
            config_path = "./config.cfg"
        if not os.path.isfile(config_path):
            ConfigHandler.gui_config_setup()  # changed from config_setup()
        else:
            cfg_file = open(config_path, "r", encoding='utf-8')
            cfg_lines = cfg_file.readlines()
            for i in enumerate(cfg_lines):
                cfg_lines[i[0]] = cfg_lines[i[0]][:-1]
            temp_dict = "{" + ", ".join(cfg_lines) + "}"
            ConfigHandler.cfg_dict = literal_eval(temp_dict)
            if not debug:
                ConfigHandler.validate_config()
            cfg_file.close()

    @staticmethod
    def validate_config():
        # Looks at the config_layout and checks if any lines are missing. If so, asks for them and saves to config
        config_layout = ConfigHandler.config_layout
        config_wasnt_valid = False
        for layout_item in config_layout.keys():
            if layout_item not in ConfigHandler.cfg_dict.keys():
                ConfigHandler.cfg_dict[layout_item] = ""
                config_wasnt_valid = True
        if ConfigHandler.cfg_dict["save password"] == "False":
            if ConfigHandler.cfg_dict["s_password"] != "":
                config_wasnt_valid = True
                ConfigHandler.cfg_dict["s_password"] = ""
        if config_wasnt_valid:
            ConfigHandler.save_config()

    @staticmethod
    def save_config():
        # Saves content of dictionary to config.cfg in correct format
        cfg_file = open("./config.cfg", "w", encoding='UTF-8')
        for key in ConfigHandler.cfg_dict:
            cfg_file.write(f'"{key}" : "{ConfigHandler.cfg_dict[key]}"\n')

    @staticmethod
    def gui_config_edit(index, entered_text=None, yes_no_value=None, browser_chosen=None):
        cfg_layout = []
        for key in ConfigHandler.config_layout.keys():
            if ConfigHandler.config_layout[key] != "secret":
                cfg_layout.append(key)

        line_selection = index
        if entered_text is not None:
            ConfigHandler.cfg_dict[cfg_layout[line_selection]] = ConfigHandler.ask_config_line(
                cfg_layout[line_selection], entered_text=entered_text)
        elif yes_no_value is not None:
            ConfigHandler.cfg_dict[cfg_layout[line_selection]] = ConfigHandler.ask_config_line(
                cfg_layout[line_selection], yes_no_value=yes_no_value)
        elif browser_chosen is not None:
            ConfigHandler.cfg_dict[cfg_layout[line_selection]] = ConfigHandler.ask_config_line(
                cfg_layout[line_selection], preferred_browser=browser_chosen)
        else:
            ConfigHandler.cfg_dict[cfg_layout[line_selection]] = ConfigHandler.ask_config_line(
                cfg_layout[line_selection])
        ConfigHandler.save_config()

    @staticmethod
    def gui_config_setup():
        cfg_layout = ConfigHandler.config_layout.keys()
        for entry in cfg_layout:
            if ConfigHandler.config_layout[entry] == "secret":
                ConfigHandler.cfg_dict[entry] = ""
                if entry == "current_theme":
                    ConfigHandler.cfg_dict[entry] = "ph"
            elif ConfigHandler.config_layout[entry] == "path":
                ConfigHandler.cfg_dict[entry] = "ENTER A PATH"
            elif ConfigHandler.config_layout[entry] == "text":
                ConfigHandler.cfg_dict[entry] = ""
            elif ConfigHandler.config_layout[entry] == "browser":
                ConfigHandler.cfg_dict[entry] = "chrome"
            elif ConfigHandler.config_layout[entry] == "yn":
                ConfigHandler.cfg_dict[entry] = False

        ConfigHandler.save_config()

    @staticmethod
    def ask_config_line(key_to_ask, entered_text=None, yes_no_value=None, preferred_browser=None):
        # Asks user to select new configuration item based on the contents of the received token
        cfg_type = ConfigHandler.config_layout[key_to_ask]
        if cfg_type == "yn":
            new_value = yes_no_value
        else:
            if cfg_type != "text":
                pass
            new_value = ""
            if cfg_type == "path":
                new_value = find_path()
            elif cfg_type == "browser":
                new_value = preferred_browser
            elif cfg_type == "text":
                new_value = entered_text

        return new_value


def validate_cfg_images():
    # Gets edited image location from the config and checks that it exists and has at least one valid file
    images_folder = read_config("edited images location")
    if images_folder == "":
        return ""
    for is_this_image in os.listdir(images_folder):
        if fnmatch.fnmatch(is_this_image, "*.jpg") or fnmatch.fnmatch(is_this_image, "*.gif"):
            return images_folder
    else:
        return ""
