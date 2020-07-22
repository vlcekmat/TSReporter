from utils import is_int, find_path
import os
import ast


class ConfigHandler:
    cfg_dict = {}

    # This is the layout of the config.cfg file by lines. Use this to inform the user or validate config.cfg
    # If a new config option needs to be added, add it here and validate_config() will automatically get it from user
    @staticmethod
    def get_config_layout():
        return (
            "trunk location",
            "documents location",
            "edited images location",
            "mantis username",
            "preferred browser",
        )

    def __init__(self):
        if not os.path.isfile("./config.cfg"):
            ConfigHandler.config_setup()
        else:
            cfg_file = open("./config.cfg", "r")
            cfg_lines = cfg_file.readlines()
            for i in enumerate(cfg_lines):
                cfg_lines[i[0]] = cfg_lines[i[0]][:-1]
            temp_dict = "{" + ", ".join(cfg_lines) + "}"
            ConfigHandler.cfg_dict = ast.literal_eval(temp_dict)
            ConfigHandler.validate_config()

    @staticmethod
    def read(key):
        return ConfigHandler.cfg_dict[key]

    # Looks at the config_layout and checks if any config lines are missing. If so, asks for them and saves to config
    @staticmethod
    def validate_config():
        config_layout = ConfigHandler.get_config_layout()
        for layout_item in config_layout:
            if layout_item not in ConfigHandler.cfg_dict.keys():
                print("Your config.cfg is missing some lines!")
                ConfigHandler.cfg_dict[layout_item] = ConfigHandler.ask_config_line(layout_item)
        ConfigHandler.save_config()

    # Lists contents of config.cfg
    @staticmethod
    def list_config():
        i = 1
        for key in ConfigHandler.cfg_dict:
            print(str(i) + ": " + key + ":\t\t" + ConfigHandler.cfg_dict[key])
            i += 1

    # Saves content of dictionary to config.cfg in correct format
    @staticmethod
    def save_config():
        cfg_file = open("./config.cfg", "w")
        for key in ConfigHandler.cfg_dict:
            cfg_file.write(f'"{key}" : "{ConfigHandler.cfg_dict[key]}"\n')
        print("Configuration changes saved")

    # Shows the contents of the config.cfg file to the user and gives them the option to edit any of the configurations
    @staticmethod
    def config_edit():
        cfg_layout = ConfigHandler.get_config_layout()
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
                ConfigHandler.save_config()
                continue

    @staticmethod
    # Opens windows dialogue windows and has the user select their Trunk, Steam and edited pictures directories
    # Then reads Mantis username from user input
    # Saves the directories to './config.cfg'
    def config_setup():
        print("No config.cfg file detected, running first time setup")
        cfg_layout = ConfigHandler.get_config_layout()
        for entry in cfg_layout:
            ConfigHandler.cfg_dict[entry] = ConfigHandler.ask_config_line(entry)
        ConfigHandler.save_config()

    # Asks user to select new configuration item based on the contents of the received token
    @staticmethod
    def ask_config_line(key_to_ask):
        print(f"Select your {key_to_ask}")
        if 'location' in key_to_ask:
            new_value = find_path()
        elif 'browser' in key_to_ask:
            new_value = ask_preferred_browser()
        else:
            new_value = input("> ")
        return new_value


# Asks user for browser
def ask_preferred_browser():
    while True:
        pref_browser = input("Do you want to use Chrome or Firefox? Type C/F\n> ")
        if pref_browser.upper() == 'C':
            return 'chrome'
        elif pref_browser.upper() == 'F':
            return 'firefox'
