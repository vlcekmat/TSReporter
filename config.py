from utils import is_int, find_path
import os
import ast


class ConfigHandler:
    cfg_dict = {}

    def __init__(self):
        if not os.path.isfile("./config_test.cfg"):
            ConfigHandler.config_setup()
        else:
            cfg_file = open("./config_test.cfg", "r")
            cfg_lines = cfg_file.readlines()
            for i in enumerate(cfg_lines):
                cfg_lines[i[0]] = cfg_lines[i[0]][:-1]
            temp_dict = "{" + ", ".join(cfg_lines) + "}"
            ConfigHandler.cfg_dict = ast.literal_eval(temp_dict)

    @staticmethod
    def read(key):
        return ConfigHandler.cfg_dict[key]

    # def validate_cfg(self):

    # Lists contents of config.cfg
    @staticmethod
    def list_config():
        i = 1
        for key in ConfigHandler.cfg_dict:
            print(str(i) + ": " + key + ":\t\t" + ConfigHandler.cfg_dict[key])
            i += 1

    # This is the layout of the config.cfg file by lines. Use this to inform the user or validate config.cfg
    @staticmethod
    def get_config_layout():
        return (
            "trunk location",
            "documents location",
            "edited images location",
            "mantis username",
            "preferred browser"
        )

    @staticmethod
    def save_config():
        cfg_file = open("./config_test.cfg", "w")
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
                print(f"Select a new {cfg_layout[ls]}")
                if "location" in cfg_layout[ls]:
                    ConfigHandler.cfg_dict[cfg_layout[ls]] = find_path()
                elif "browser" in cfg_layout[ls]:
                    ConfigHandler.cfg_dict[cfg_layout[ls]] = ask_preferred_browser()
                else:
                    ConfigHandler.cfg_dict[cfg_layout[ls]] = input("> ")
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
            print(f"Select your {entry}")
            new_value = ""
            if 'location' in entry:
                new_value = find_path()
            elif 'browser' in entry:
                new_value = ask_preferred_browser()
            else:
                new_value = input("> ")
            ConfigHandler.cfg_dict[entry] = new_value
        ConfigHandler.save_config()


# This is the layout of the config.cfg file by lines. Use this to inform the user.
def get_config_layout():
    return {
        1: "trunk location",
        2: "documents location",
        3: "edited images location",
        4: "mantis username",
        5: "preferred browser"
    }


# Shows the contents of the config.cfg file to the user and gives them the option to edit any of the configurations
def config_edit():
    if not os.path.isfile("./config.cfg"):
        config_setup()
        return
    config_file = open("./config.cfg", "r")
    config_lines = config_file.readlines()
    config_file.close()
    cfg_layout = get_config_layout()
    while True:
        print("These is your current configuration, type the number of what you want to modify:")
        print("0: Exit config")
        for _i in range(0, len(config_lines)):  # Print out the current configuration
            print(f"{_i + 1}: {cfg_layout[_i + 1]}:\t{config_lines[_i][:-1]}")
        line_selection = input("> ")
        if not is_int(line_selection) or not 0 <= int(line_selection) <= len(cfg_layout):
            print("Invalid choice")
            continue
        elif int(line_selection) == 0:
            break
        else:
            print(f"Select a new {cfg_layout[int(line_selection)]}")
            if "location" in cfg_layout[int(line_selection)]:
                config_lines[int(line_selection) - 1] = find_path() + '\n'
            elif "browser" in cfg_layout[int(line_selection)]:
                config_lines[int(line_selection) - 1] = ask_preferred_browser()
            else:
                config_lines[int(line_selection) - 1] = input("> ") + '\n'
            continue
    config_file = open("./config.cfg", "w")
    config_file.writelines(config_lines)
    config_file.close()
    print("Configuration changes saved")


# Asks user for browser
def ask_preferred_browser():
    while True:
        pref_browser = input("Do you want to use Chrome or Firefox? Type C/F\n> ")
        if pref_browser.upper() == 'C':
            return 'chrome'
        elif pref_browser.upper() == 'F':
            return 'firefox'


# Opens windows dialogue windows and has the user select their Trunk, Steam and edited pictures directories
# Then reads Mantis username from user input
# Saves the directories to './config.cfg'
def config_setup():
    print("No config.cfg file detected, running first time setup")
    write_us = []
    cfg_layout = get_config_layout()
    for i in range(1, 4):
        print(f"Select your {cfg_layout[i]}")
        write_us.append(find_path() + '\n')
    login_name = input("Enter your Mantis username.\n> ")
    write_us.append(login_name + '\n')
    while True:
        pref_browser = input("Do you want to use Chrome or Firefox? Type C/F\n> ")
        if pref_browser.upper() == 'C':
            write_us.append('chrome\n')
            break
        elif pref_browser.upper() == 'F':
            write_us.append('firefox\n')
            break

    config_file = open("./config.cfg", "w")
    config_file.writelines(write_us)
    config_file.close()


#cfgh = ConfigHandler()
#cfgh.config_edit()
