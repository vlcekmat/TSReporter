import requests


def clean_sector(log_line):
    # Extracts the sector from the log line
    line_segment = log_line.split(';')[1]
    sector = line_segment.split('(')[1][:-1]
    return sector


def request_sector_owner(sector_to_find, game):
    # Requests the sector owner from the games' url using POST
    if game == 'A':
        get_owner_url = "http://map.scs/usa/get_sector_owner.php?"
    else:
        get_owner_url = "http://map.scs/europe/get_sector_owner.php"
    headers = {"Accept": "application/json"}
    data = {"sectors": sector_to_find}
    reply = requests.post(get_owner_url, headers=headers, data=data)
    js = reply.json()
    try:
        sector_owner = js[sector_to_find]["owner"]["svn_name"]
        return sector_owner
    except KeyError:
        return ""


def get_asset_assign_dict():
    # This lists the people responsible for different types of assets in both games
    # taken from the testing guide on wiki (currently at http://wiki.scs/wiki/User:Adam_Fojtik)
    return(
        {"A": {
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
         }}
    )


def ask_asset_type():
    # Asks user for what type of asset the bug is. Used when asset type is not specified in bugs.txt line
    while True:
        type_of_asset = input("> ")
        if type_of_asset in ["r", "v", "c", "a"]:
            return type_of_asset


def find_assign_to(line, chosen_game):
    # Assignee is found here. Map bugs are found using the get_sector_owner page
    # assets are determined based on their game and asset type, other unknown reports are default blank
    bug_type = line.split('_', maxsplit=1)[0]
    assign_to = ""
    if bug_type == "m":
        get_owner_of_this = clean_sector(line)
        assign_to = request_sector_owner(get_owner_of_this, chosen_game)
    elif bug_type in ["ar", "av", "ac", "aa"]:
        ass_dict = get_asset_assign_dict()
        assign_to = ass_dict[chosen_game][bug_type]

    return assign_to
