from pathlib import Path
from collections import deque


# returns a Path() of the particular image file based on date, time and coordinates
def get_image(log, images_folder_path):
    split_log = log.split(';')

    raw_date_time = split_log[1][1 : 17]
    split_date = raw_date_time.split(' ')[0].split('/')
    split_time = raw_date_time.split(' ')[1].split(':')
    date_time_to_find = f'{split_date[2]}{split_date[1]}{split_date[0]}_{split_time[0]}{split_time[1]}'

    coordinates_to_find = str(round(float(split_log[2]))) + '_' + str(round(float(split_log[3]))) + '_' + str(round(float(split_log[4])))

    path = Path(images_folder_path)
    for file in path.glob('*.jpg') or path.glob('*.gif'):
        if date_time_to_find in file.name and coordinates_to_find in file.name:
            return file
        else:
            pass
    return ""


# returns 'm' for map, 'a' for asset
def determine_bug_category(log):
    split_log = log.split(';')
    if "_" not in split_log[0]:
        return ""
    category = split_log[0].split('_', maxsplit=1)[0]
    if category in ["m", "a"]:
        return category
    elif category in ["aa", "ar", "av", "ac"]:
        return category[0]


# puts information from main in a cohesive report and returns it
def generate_description(line, version, category, asset='', first_time=False):
    split_log = line.split(';')
    if '_' in split_log[0]:
        log_without_category = ''.join(split_log[0].split('_', maxsplit=1)[1]) + ';' + ''.join(split_log[1]) + ';' + ';'.join(
            split_log[2:])
    elif '.' in split_log[0]:
        log_without_category = ''.join(split_log[0].split('.', maxsplit=1)[1]) + ';' + ''.join(split_log[1]) + ';' + ';'.join(
            split_log[2:])
    else:
        log_without_category = line
    if category == 'a' and first_time:
        first_time = False
        report_description = f'''{version} - {log_without_category}
PATH TO THE ASSET: {asset}'''

    else:
        report_description = f'''{version} - {log_without_category}'''

    return report_description


# cuts the version off the given description
def generate_no_version_des(description):
    no_ver_des = ''.join(description).split('] - ')[1:]
    return no_ver_des


# uses log line (bug_description) to gather sector and the first two letters of coordinates
def extract_location_filter(bug_description):
    time_sector = bug_description.split(';')[1]  # Generates a filter to use in mantis for the duplicate check
    sector = time_sector.split(' ')[2]
    first_two_coordinates = bug_description.split(';')[2][:2]
    if first_two_coordinates[0] == '-':
        first_two_coordinates = bug_description.split(';')[2][:3]
    else:
        pass
    final_filter = f'{sector};{first_two_coordinates}'
    return final_filter


# so from '/model/advert/billboard/billboard_uni_astand.pmd' it will return 'billboard_uni_astand'
def extract_asset_name(path_to_asset):
    asset_name_suffix = path_to_asset.split('/')[-1]
    asset_name = asset_name_suffix.split('.')[0]
    return asset_name


# returns path to the asset
def extract_asset_path(debug_info):
    asset_path = ''
    for part in debug_info.split(' '):
        if '/' in part:
            asset_path = part.split("'")[1]
    return asset_path
