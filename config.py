import fnmatch
from ast import literal_eval

from utils import find_path
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
            "s_password": "secret;hash",
            "current theme": "secret;theme",
            # "renamed images location": "path"
            "custom theme": "secret;color"
    }

    def __init__(self, debug=False):
        if debug:
            config_path = "tests/config.cfg"
        else:
            config_path = "./config.cfg"
        if not os.path.isfile(config_path):
            self.gui_config_setup()
        else:
            cfg_file = open(config_path, "r", encoding='utf-8')
            cfg_lines = cfg_file.readlines()
            for i in enumerate(cfg_lines):
                cfg_lines[i[0]] = cfg_lines[i[0]][:-1]
            temp_dict = "{" + ", ".join(cfg_lines) + "}"
            ConfigHandler.cfg_dict = literal_eval(temp_dict)
            if not debug:
                self.validate_config()
            cfg_file.close()

    def validate_config(self):
        # Looks at the config_layout and checks if any lines are missing. If so, asks for them and saves to config
        config_layout = ConfigHandler.config_layout
        config_wasnt_valid = False
        for layout_item in config_layout.keys():
            if layout_item not in ConfigHandler.cfg_dict.keys():
                # ConfigHandler.cfg_dict[layout_item] = ""
                ConfigHandler.cfg_dict[layout_item] = self.get_default_config_value(config_layout[layout_item])
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
            if "secret" not in ConfigHandler.config_layout[key]:
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
    def get_default_config_value(config_line_type):
        if "path" in config_line_type:
            return "ENTER A PATH"
        elif "text" in config_line_type:
            return ""
        elif "browser" in config_line_type:
            return "chrome"
        elif "yn" in config_line_type:
            return False
        elif "color" in config_line_type:
            return "#ffffff;#ffffff;#ffffff;#ffffff"
        elif "current theme" in config_line_type:
            return "ph"
        else:
            return ""

    def gui_config_setup(self):
        cfg_layout = ConfigHandler.config_layout.keys()
        for entry in cfg_layout:
            if "secret" in ConfigHandler.config_layout[entry]:
                ConfigHandler.cfg_dict[entry] = ""
            else:
                ConfigHandler.cfg_dict[entry] = self.get_default_config_value(ConfigHandler.config_layout[entry])
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


def get_custom_theme():
    theme_str = read_config("custom theme")
    custom_theme = []
    for color in theme_str.split(';'):
        custom_theme.append(color)
    if len(custom_theme) == 4:
        return custom_theme
    else:
        return ['#ffffff', '#ffffff', '#ffffff', '#ffffff']


def get_theme(theme):
    theme_dict = {
        "ph": [
            # Change the values below to change the overall color theme of the app
            'white',  # Regular Buttons
            '#ffa500',  # Quit Button, text
            '#484848',  # Integrated Frames
            '#2B2B2B'  # Background
        ],

        "campfire": [
            # Change the values below to change the overall color theme of the app
            '#03A678',  # Regular Buttons
            '#F28C0F',  # Quit Button, text
            '#02735E',  # Integrated Frames
            '#014040'  # Background
        ],

        "hazard_theme": [
            # Change the values below to change the overall color theme of the app
            '#BD554A',  # Regular Buttons
            '#CF423C',  # Quit Button, text
            '#570B2A',  # Integrated Frames
            '#33081E'  # Background
        ],

        "candle": [
            # Change the values below to change the overall color theme of the app
            '#6EAFB5',  # Regular Buttons
            '#FD9F75',  # Quit Button, text
            '#185572',  # Integrated Frames
            '#05395E'  # Background
        ],

        "navy": [
            # Change the values below to change the overall color theme of the app
            '#387097',  # Regular Buttons
            'white',  # Quit Button, text
            '#1F384C',  # Integrated Frames
            '#1B2838'  # Background
        ],

        "purple_rain": [
            # Change the values below to change the overall color theme of the app
            '#ECE8E1',  # Regular Buttons
            '#FF4655',  # Quit Button, text
            '#8C3243',  # Integrated Frames
            '#271D26'  # Background
        ],

        "storm": [
            # Change the values below to change the overall color theme of the app
            '#908CAC',  # Regular Buttons
            '#C3BBD2',  # Quit Button, text
            '#3F384F',  # Integrated Frames
            '#1A1E26'  # Background
        ],

        "grayscale": [
            # Change the values below to change the overall color theme of the app
            '#838383',  # Regular Buttons
            '#D9D9D9',  # Quit Button, text
            '#404040',  # Integrated Frames
            '#262626'  # Background
        ]
    }
    if theme == 'all':
        return theme_dict
    if theme == 'custom':
        return get_custom_theme()
    elif theme and theme_dict[theme]:
        return theme_dict[theme]
    else:
        return theme_dict["ph"]
