from pathlib import Path
from decimal import Decimal
from config import read_config


def _time_format_error():
    print("WARNING, unknown date/time format. The bugs.txt time format must have changed. "
          "Contact a programmer to fix this.")


def get_image(log):
    # returns a Path() of the particular image file based on date, time and coordinates
    images_folder_path = read_config("edited images location")
    split_log = log.split(';')

    # ...;[28/08/2021 14:21] (sec-0019-0008);... -> 28/08/2021 14:21
    raw_dt = split_log[1].split(']')[0][1:]
    if '/' not in raw_dt or ':' not in raw_dt:
        _time_format_error()
        return None

    s_date = raw_dt.split(' ')[0].split('/')
    s_time = raw_dt.split(' ')[1].split(':')

    if len(s_time) == 3:
        date_time_to_find = f'{s_date[2]}{s_date[1]}{s_date[0]}_{s_time[0]}{s_time[1]}{s_time[2]}'
    elif len(s_time) == 2 and len(s_date) == 3:
        date_time_to_find = f'{s_date[2]}{s_date[1]}{s_date[0]}_{s_time[0]}{s_time[1]}'
    else:
        _time_format_error()
        return None

    coord_0 = str(round(Decimal(str(split_log[2]))))[:-1]
    coord_2 = str(round(Decimal(str(split_log[4]))))[:-1]

    path = Path(images_folder_path)
    for file in path.glob('*.gif'):
        if date_time_to_find in file.name and coord_0 in file.name and coord_2 in file.name:
            return file
        elif date_time_to_find in file.name and str((int(coord_0) - 1)) in file.name and coord_2 in file.name:
            return file
        elif date_time_to_find in file.name and str((int(coord_0) + 1)) in file.name and coord_2 in file.name:
            return file
    for file in path.glob('*.jpg'):
        if date_time_to_find in file.name and coord_0 in file.name and coord_2 in file.name:
            return file
        elif date_time_to_find in file.name and str((int(coord_0) - 1)) in file.name and coord_2 in file.name:
            return file
        elif date_time_to_find in file.name and str((int(coord_0) + 1)) in file.name and coord_2 in file.name:
            return file
    return ""


def determine_bug_category(log):
    # returns 'm' for map, 'a' for asset
    split_log = log.split(';')
    if "_" in split_log[0]:
        category = split_log[0].split('_', maxsplit=1)[0]
        if category in ["m", "a", "aa", "ar", "av", "ac"]:
            return category
    return ""


def generate_description_line(line):
    # puts information from main in a cohesive report and returns it
    split_log = line.split(';')
    if split_log[0][0] == '.':
        split_log[0] = split_log[0][1:]
        log_without_category = ';'.join(split_log)
    elif '_' in split_log[0]:  # First join is there to convert array to string easily
        log_without_category = ''.join(split_log[0].split('_', maxsplit=1)[1]) + ';' + ';'.join(split_log[1:])
    else:
        log_without_category = line
    return log_without_category


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
    asset_file = path_to_asset.split('/')[-1]
    if '.' in asset_file:
        asset_name = asset_file.split('.')[0]
    else:
        asset_name = asset_file
    return asset_name


def extract_asset_path(debug_info):
    # accepts DEBUG INFO and returns path to the asset
    asset_path = ''
    for part in debug_info.split(' '):
        if '/' in part:
            asset_path = part.split("'")[1]
            break
    return asset_path


def clean_debug_info(debug_info):
    # Removes time from debug info line
    if ' : ' not in debug_info:
        return debug_info
    else:
        debug_info_out = debug_info.split(' : ', maxsplit=1)[1]
        return debug_info_out
