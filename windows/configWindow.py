import PySimpleGUIQt as sg
from utils import get_config_options
import json


def config_window():
    layout = [
        [
            sg.Text("Enter Entire Cluster Folder", justification='c')
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
            sg.Button("Close", key="close", enable_events=True)
        ]
    ]
    c_window = sg.Window("Config", layout=layout)
    while True:
        event, values = c_window.read()

        if event == sg.WINDOW_CLOSED or event == "close":
            c_window.close()
            break
        elif event == "list_box":
            print(values["list_box"])
            try:
                x = values["list_box"][0].split(" | ")
                c_window["folder_in"].update(x[1])
                c_window["option_select"].update(x[0])
            except IndexError:
                c_window["folder_in"].update('')
                c_window["option_select"].update('')
            c_window.refresh()

        elif event == "add":
            with open('config.json', 'r') as file:
                data = json.loads(file.read())
            data["servers"][values["option_select"]] = {"location": f"{values['folder_in']}"}
            with open("config.json", "w") as file:
                json.dump(data, file, indent=2)
            c_window["list_box"].update(get_config_options())
            c_window.refresh()
        elif event == "remove":
            with open("config.json", "r") as file:
                data = json.loads(file.read())
            try:
                del data["servers"][values["option_select"]]
                with open("config.json", "w") as file:
                    json.dump(data, file, indent=2)
                c_window["list_box"].update(get_config_options())
                c_window.refresh()
            except KeyError:
                continue
