import json


def get_config_options():
    with open("config.json", "r") as file:
        data = json.loads(file.read())
    servers = data["servers"]
    names = []
    paths = []
    for name, value in servers.items():
        names.append(name)
        for loc, path in value.items():
            paths.append(path)
    final = []
    num = 0
    for n in names:
        final.append(f"{n} | {paths[num]}")
        num += 1

    return final


def get_data():
    with open("config.json", "r") as file:
        data = json.loads(file.read())
    return data


def get_admins():
    data = get_data()
    admins = []
    try:
        x = data["admins"]
    except KeyError:
        data["admins"] = {}
        with open("config.json", "w") as file:
            json.dump(data, file, indent=2)
    for [key, value] in data["admins"].items():
        admins.append(key)
    return admins


def get_admin_names():
    data = get_data()
    admins = []
    try:
        x = data["admins"]
    except KeyError:
        data["admins"] = {}
        with open("config.json", "w") as file:
            json.dump(data, file, indent=2)
    for [key, value] in data["admins"].items():
        admins.append(value)
    return admins


def check_steam_id(steamid):
    status = False
    try:
        if len(steamid) == 17:
            steamid = int(steamid)
            status = True
    except Exception as e:
        print(e)
    return status
