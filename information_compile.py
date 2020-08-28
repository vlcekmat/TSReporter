from pathlib import Path
from decimal import Decimal
from config import read_config


def get_image(log):
    # returns a Path() of the particular image file based on date, time and coordinates
    images_folder_path = read_config("edited images location")
    split_log = log.split(';')

    raw_date_time = split_log[1][1: 17]
    split_date = raw_date_time.split(' ')[0].split('/')
    split_time = raw_date_time.split(' ')[1].split(':')
    date_time_to_find = f'{split_date[2]}{split_date[1]}{split_date[0]}_{split_time[0]}{split_time[1]}'
    coord_0 = str(round(Decimal(str(split_log[2]))))[:-1]
    coord_2 = str(round(Decimal(str(split_log[4]))))[:-1]

    if '-' in coord_2:
        coord_2 = str(round(Decimal(str(split_log[4]))))[:6]

    path = Path(images_folder_path)
    for file in path.glob('*.gif'):
        if date_time_to_find in file.name and coord_0 in file.name and coord_2 in file.name:
            return file
        else:
            pass
    for file in path.glob('*.jpg'):
        if date_time_to_find in file.name and coord_0 in file.name and coord_2 in file.name:
            return file
        else:
            pass
    return ""


def determine_bug_category(log):
    # returns 'm' for map, 'a' for asset
    split_log = log.split(';')
    if "_" not in split_log[0]:
        return ""
    category = split_log[0].split('_', maxsplit=1)[0]

    if category in ["m", "a"]:
        return category
    elif category in ["aa", "ar", "av", "ac"]:
        return category[0]
    else:
        return ""


def generate_description(line):
    # puts information from main in a cohesive report and returns it
    split_log = line.split(';')
    if '_' in split_log[0]:  # First join is there to convert array to string easily
        log_without_category = ''.join(split_log[0].split('_', maxsplit=1)[1]) + ';' + ';'.join(split_log[1:])
    elif '.' in split_log[0]:
        log_without_category = ''.join(split_log[0][1:]) + ';' + ';'.join(split_log[1:])
    else:
        log_without_category = line
    return log_without_category


def generate_no_version_des(description):
    # cuts the version off the given description
    no_ver_des_field = ''.join(description).split('] - ')[1:]
    no_ver_des = ''.join(no_ver_des_field)
    return no_ver_des


def extract_location_filter(bug_description):
    # uses log line (bug_description) to gather sector and the first two letters of coordinates
    time_sector = bug_description.split(';')[1]  # Generates a filter to use in mantis for the duplicate check
    sector = time_sector.split(' ')[2]
    first_two_coordinates = bug_description.split(';')[2][:2]
    if first_two_coordinates[0] == '-':
        first_two_coordinates = bug_description.split(';')[2][:3]
    else:
        pass
    final_filter = f'{sector};{first_two_coordinates}'
    return final_filter


def extract_asset_name(path_to_asset):
    # From '/model/advert/billboard/billboard_uni_astand.pmd' it will return 'billboard_uni_astand'
    asset_name_suffix = path_to_asset.split('/')[-1]
    asset_name = asset_name_suffix.split('.')[0]
    return asset_name


def extract_asset_path(debug_info):
    # accepts DEBUG INFO and returns path to the asset
    asset_path = ''
    for part in debug_info.split(' '):
        if '/' in part:
            asset_path = part.split("'")[1]
    return asset_path


def clean_debug_info(debug_info):
    # Removes time from debug info line
    if ' : ' not in debug_info:
        return debug_info
    else:
        debug_info_out = debug_info.split(' : ', maxsplit=1)[1]
        return debug_info_out
