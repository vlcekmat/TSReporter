import requests


def clean_sector(log_line):
    # Extracts the sector from the log line
    line_segment = log_line.split(';')[1]
    sector = line_segment.split('(')[1][:-1]
    return sector


def request_sector_owner(sector_to_find, game, svn_not_found=False):
    # Requests the sector owner from the games' url using POST
    if game == 'A':
        get_owner_url = "http://map.scs/usa/get_sector_owner.php?"
    else:
        get_owner_url = "http://map.scs/europe/get_sector_owner.php"
    headers = {"Accept": "application/json"}
    data = {"sectors": sector_to_find}
    reply = requests.post(get_owner_url, headers=headers, data=data)
    js = reply.json()
    try:  # Timmy made the server part of this if something breaks, go see him
        if svn_not_found:
            sector_owner = js[sector_to_find]["owner"]["username"]
        else:
            sector_owner = js[sector_to_find]["owner"]["svn_name"]
    except KeyError:
        return ""
    return sector_owner.lower()


def get_asset_assign(chosen_game, bug_type):
    # This lists the people responsible for different types of assets in both games
    # taken from the testing guide on wiki (currently at http://wiki.scs/wiki/Testing_Guide)
    # If there's a change, this will need to be changed as well!
    ass_dict = {
            "A": {
                "ar": "milan.lukes",
                "av": "Arthur",
                "ac": "ondrej.hejbal",
                "aa": "jupiter"
            },
            "E": {
                "ar": "jiri.dosedel",
                "av": "Arthur",
                "ac": "ondrej.hejbal",
                "aa": "martin.vocet"
            }
        }
    return ass_dict[chosen_game][bug_type]


def find_assign_to(line, chosen_game, svn_not_found=False):
    # Assignee is found here. Map bugs are found using the get_sector_owner page
    # assets are determined based on their game and asset type, other unknown reports are default blank
    assign_to = ""
    if '_' in line:
        bug_type = line.split('_', maxsplit=1)[0]
        if bug_type == "m":
            get_owner_of_this = clean_sector(line)
            assign_to = request_sector_owner(get_owner_of_this, chosen_game, svn_not_found=svn_not_found)
        elif bug_type in ["ar", "av", "ac", "aa"]:
            assign_to = get_asset_assign(chosen_game, bug_type)
    return assign_to
