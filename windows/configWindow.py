import PySimpleGUIQt as sg
from utils import get_config_options, get_data, get_admins, get_admin_names, check_steam_id
import json

def get_layout():
    layout = [
        [
            sg.Text("Enter Each Entire Cluster Folder", justification='c')
        ],
        [
            sg.Listbox(values=get_config_options(), size=(600, 300), enable_events=True, key="list_box")
        ],
        [
            sg.InputText(key="option_select", enable_events=True, size=(10, .7)),
            sg.In(key="folder_in", disabled=True, enable_events=True),
            sg.FolderBrowse()
        ],
        [
            sg.HSeperator()
        ],
        [
            sg.Button("Add", key="add", enable_events=True),
            sg.Button("Remove", key="remove", enable_events=True)
        ],
        [
            sg.HSeperator()
        ],
        [
          sg.Text("Enter All Admin Steam IDs", justification='c')
        ],
        [
            sg.Listbox(values=get_admins(), size=(300, 300), key="admin_list", enable_events=True),
            sg.Listbox(values=get_admin_names(), size=(300, 300), key="admin_names", enable_events=True)
        ],
        [
            sg.In(default_text="Enter SteamID", size=(25, .7), key="admin_input"),
            sg.In(default_text="Name Not Set", size=(25, .7), key="admin_name_input"),
            sg.Button("Add", key="add_admin"),
            sg.Button("Remove", key="remove_admin")
        ],
        [
          sg.HSeperator()
        ],
        [
            sg.Button("Close", key="close", enable_events=True)
        ]
    ]
    return layout


def config_window():
    window = sg.Window("Config", layout=get_layout())
    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED or event == "close":
            window.close()
            break
        elif event == "list_box":
            try:
                x = values["list_box"][0].split(" | ")
                window["folder_in"].update(x[1])
                window["option_select"].update(x[0])
            except IndexError:
                window["folder_in"].update('')
                window["option_select"].update('')
            window.refresh()

        elif event == "add":
            data = get_data()
            data["servers"][values["option_select"]] = {"location": f"{values['folder_in']}"}
            with open("config.json", "w") as file:
                json.dump(data, file, indent=2)
            window["list_box"].update(get_config_options())
            window.refresh()
        elif event == "remove":
            data = get_data()
            try:
                del data["servers"][values["option_select"]]
                with open("config.json", "w") as file:
                    json.dump(data, file, indent=2)
                window["list_box"].update(get_config_options())
                window.refresh()
            except KeyError:
                continue
        elif event == "admin_list":
            if not values["admin_list"]:
                continue
            try:
                data = get_data()
                admins = []
                for [key, value] in data["admins"].items():
                    admins.append(key)
                admin = values["admin_list"][0]
                window["admin_input"].update(admin)
                window["admin_names"].update(set_to_index=admins.index(admin))
                window.refresh()
            except IndexError:
                continue

        elif event == "admin_names":
            if not values["admin_names"]:
                continue
            data = get_data()
            admins = []
            for [key, value] in data["admins"].items():
                admins.append(value)
            admin = values["admin_names"][0]
            window["admin_name_input"].update(admin)
            window["admin_list"].update(set_to_index=admins.index(admin))
            window.refresh()

        elif event == "add_admin":
            data = get_data()
            new_admin = values["admin_input"] or None
            new_admin_name = values["admin_name_input"] or None
            if new_admin is None or new_admin_name is None:
                sg.PopupQuickMessage("Fields Empty!", background_color='black')
                continue
            admins = get_admins()
            admin_names = get_admin_names()
            if new_admin not in admins and check_steam_id(values["admin_input"]):
                admins.append(values["admin_input"])
                admin_names.append(values["admin_name_input"])
                new_admins = dict(zip(admins, admin_names))
                data["admins"] = new_admins
                with open("config.json", "w") as file:
                    json.dump(data, file, indent=2)

                window["admin_list"].update(admins)
                window["admin_names"].update(admin_names)
                window["admin_input"].update('')
                window["admin_name_input"].update('')
                window.refresh()
            else:
                sg.PopupQuickMessage("Invalid SteamID", background_color='black')
                window["admin_input"].update('')
                window["admin_name_input"].update('')
                window.refresh()

        elif event == "remove_admin":
            data = get_data()
            new_admin = values["admin_input"] or None
            new_admin_name = values["admin_name_input"] or None
            if new_admin is not None or new_admin_name is not None:
                admins = get_admins()
                admin_names = get_admin_names()
                if new_admin in admins:
                    admin_names.remove(admin_names[admins.index(new_admin)])
                    admins.remove(new_admin)
                    new_admins = dict(zip(admins, admin_names))
                    data["admins"] = new_admins
                    with open("config.json", "w") as file:
                        json.dump(data, file, indent=2)

                    window["admin_list"].update(admins)
                    window["admin_names"].update(admin_names)
                    window["admin_input"].update('')
                    window["admin_name_input"].update('')
                    window.refresh()
            else:
                sg.PopupQuickMessage("Fields Empty!", background_color='Black')
