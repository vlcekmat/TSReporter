from utils import is_int, find_path
import os


# This is the layout of the config.cfg file by lines. Use this to inform the user.
def get_config_layout():
    return {
        1: "Trunk location",
        2: "Documents location",
        3: "Edited images location",
        4: "Mantis username",
        5: "Preferred browser"
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
        for _i in range(0, len(config_lines)):
            print(f"{_i+1}: {cfg_layout[_i+1]}:\t{config_lines[_i][:-1]}")
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
                while True:
                    pref_browser = input("Do you want to use Chrome or Firefox? Type C/F\n> ")
                    if pref_browser.upper() == 'C':
                        config_lines[int(line_selection) - 1] = 'chrome\n'
                        break
                    elif pref_browser.upper() == 'F':
                        config_lines[int(line_selection) - 1] = 'firefox\n'
                        break
            else:
                config_lines[int(line_selection) - 1] = input("> ") + '\n'
            continue
    config_file = open("./config.cfg", "w")
    config_file.writelines(config_lines)
    config_file.close()
    print("Configuration changes saved")


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


