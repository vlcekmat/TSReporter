import requests


# Extracts the sector from the log line
def clean_sector(log_line):
    line_segment = log_line.split(';')[1]
    sector = line_segment.split('(')[1][:-1]
    return sector


# Requests the sector owner from the games' url using POST
def request_sector_owner(sector_to_find, game):
    if game == 'A':
        get_owner_url = "http://map.scs/usa/get_sector_owner.php?"
    else:
        get_owner_url = "http://map.scs/europe/get_sector_owner.php"
    headers = {"Accept": "application/json"}
    data = {"sectors": sector_to_find}
    reply = requests.post(get_owner_url, headers=headers, data=data)
    js = reply.json()
    sector_owner = js[sector_to_find]["owner"]["svn_name"]
    print(f"Owner of sector ({sector_to_find}) found: {sector_owner}")
    return sector_owner


# This lists the people responsible for different types of assets in both games
# taken from the testing guide on wiki (currently at http://wiki.scs/wiki/User:Adam_Fojtik)
def get_asset_assign_dict():
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


# Asks user for what type of asset the bug is. Used when asset type is not specified in bugs.txt line
def ask_asset_type():
    print("What kind of asset is this?")
    while True:
        print("r: roads, v: vegetation, c: animated characters, a:other")
        type_of_asset = input("> ")
        if type_of_asset in ["r", "v", "c", "a"]:
            return type_of_asset


# Assignee is found here. Map bugs are found using the get_sector_owner page
# assets are determined based on their game and asset type, other unknown reports are default blank
def find_assign_to(line, chosen_game):
    bug_type = line.split('_', maxsplit=1)[0]

    if bug_type == "m":
        get_owner_of_this = clean_sector(line)
        print(f"Looking for owner of sector ({get_owner_of_this})")
        assign_to = request_sector_owner(get_owner_of_this, chosen_game)
    elif bug_type in ["ar", "av", "ac", "aa"]:
        ass_dict = get_asset_assign_dict()
        assign_to = ass_dict[chosen_game][bug_type]
    elif bug_type == "a":
        bug_type += ask_asset_type()
        ass_dict = get_asset_assign_dict()
        assign_to = ass_dict[chosen_game][bug_type]
    else:
        assign_to = ""

    return assign_to
