import os
import shutil
import subprocess

import PySimpleGUIQt as sg
import json
from time import sleep
from windows.configWindow import config_window
from utils import get_data
import psutil


def get_server_radio():
    with open("config.json", "r") as file:
        data = json.loads(file.read())
    raw_servers = data["servers"].items()
    servers = []
    num = 1
    for x in raw_servers:
        if num == 1:
            servers.append(sg.Radio(x[0], 
                                    "servers",
                                     key=f"server_radio_{num}",
                                      enable_events=True,
                                       default=True))
        else:
            servers.append(sg.Radio(x[0],
                                     "servers",
                                      key=f"server_radio_{num}", 
                                      enable_events=True))
        num += 1
    return servers


def get_folder():
    with open("config.json", "r") as file:
        data = json.loads(file.read())

    try:
        x = data["folder"]
        if x == "":
            x = "Select folder where plugins will be pre-loaded"
        return x
    except KeyError:
        return "Select folder where plugins will be pre-loaded"


def get_server_checkboxes():
    with open("config.json", "r") as file:
        data = json.loads(file.read())
    try:
        try:
            files = os.listdir(data["folder"])
        except FileNotFoundError:
            files = ["None"]
            data["folder"] = ""
            with open("config.json", "w") as file:
                json.dump(data, file, indent=2)
        items = []
        for x in files:
            if os.path.isdir(data["folder"] + "\\" + x):
                items.append(x + " (Folder)")
            else:
                if x == "AllowedCheaterSteamIDs.txt":
                    continue
                items.append(x)
        x = [sg.MultilineOutput("\n".join(items), key="file_output")]
        return x
    except KeyError:
        return


def replace_dll(folder):
    for file in os.listdir(folder):
        if os.path.isdir(os.path.join(folder, file)):
            replace_dll(os.path.join(folder, file))
        if file.endswith(".dll"):
            shutil.move(os.path.join(folder, file), os.path.join(folder, file + ".ArkApi"))


def recursive_file_move(src, dst):
    if os.path.isdir(src):
        try:
            extra = src.split('\\')[1]
            shutil.copytree(src, dst + '\\' + extra)
        except FileExistsError:
            for file in os.listdir(src):
                extra = src.split('\\')[1]
                recursive_file_move(os.path.join(src, file), os.path.join(dst + '\\' + extra, file))
    else:
        try:
            shutil.copy(src, dst)
        except:
            pass


def get_paths(num, admin):
    with open("config.json", "r") as file:
        data = json.loads(file.read())
    server_names = []
    for key in data["servers"]:
        server_names.append(key)
    try:
        cluster = data["servers"][server_names[num]]["location"]
    except:
        pass
    paths = []
    try:
        for file in os.listdir(cluster):
            if admin:
                map_path = f"{cluster}\\{file}\\ShooterGame\\Saved"
            else:
                map_path = f"{cluster}\\{file}\\ShooterGame\\Binaries\\Win64\\ArkApi\\Plugins"
            paths.append(map_path)
    except:
        pass
    return paths


def recursive_backup(src, dst, added):
    for file in os.listdir(src):
        if os.path.isdir(f"{src}\\{file}"):
            try:
                shutil.copytree(f"{src}\\{file}", f"{dst}\\{added}\\{file}")
            except FileExistsError:
                recursive_backup(f"{src}\\{file}", f"{dst}\\{added}\\{file}", file)
        else:
            shutil.copy(f"{src}\\{file}", f"{dst}\\{added}\\{file}")


def create_backups(servers, dst, map_name, admin):
    backup_path = f"{os.curdir}\\{map_name}_backups"
    if not os.path.exists(backup_path):
        os.mkdir(f"{os.curdir}\\{map_name}_backups")
    if admin:
        try:
            shutil.copy(f"{servers[0]}\\AllowedCheaterSteamIDs.txt", f"{backup_path}\\AllowedCheaterSteamIDs.txt")
        except FileNotFoundError:
            pass
    else:
        for file in os.listdir(backup_path):
            for d in os.listdir(dst):
                if file == d:
                    if file == "AllowedCheaterSteamIDs.txt":
                        continue
                    if os.path.isdir(f"{backup_path}\\{file}"):
                        shutil.rmtree(f"{backup_path}\\{file}")
                    else:
                        os.remove(f"{backup_path}\\{file}")
        for item in os.listdir(servers[0]):
            for d in os.listdir(dst):
                if item == d:
                    try:
                        shutil.copytree(f"{servers[0]}\\{item}", f"{backup_path}\\{item}")
                    except FileExistsError:
                        for file in os.listdir(f"{servers[0]}\\{item}"):
                            if os.path.isdir(f"{servers[0]}\\{item}\\{file}"):
                                if not os.path.exists(f"{backup_path}\\{item}\\{file}"):
                                    os.mkdir(f"{backup_path}\\{item}\\{file}")
                            if os.path.isdir(f"{servers[0]}\\{item}\\{file}"):
                                recursive_backup(f"{servers[0]}\\{item}\\{file}", backup_path, f"{item}\\{file}")
                            else:
                                shutil.copy(f"{servers[0]}\\{item}\\{file}", f"{backup_path}\\{item}\\{file}")


def main():
    if "version.json" not in os.listdir(os.curdir):
        with open("version.json", "w") as file:
            data = {"version": "0.0"}
            json.dump(data, file, indent=2)
    if "config.json" not in os.listdir(os.curdir):
        with open("config.json", "w") as file:
            data = {"servers": {"tempname": {"location": "templocation"}}, "folder": "", "admins": {}}
            json.dump(data, file, indent=2)
    with open("version.json", "r") as file:
        raw_version = json.loads(file.read())
    version = raw_version["version"]
    with open("config.json", "r") as file:
        data = json.loads(file.read())
    layout = [
        [
            sg.Button("Config Options", key="config_options", enable_events=True),
            sg.Button("Reload", key="reload", enable_events=True)
        ],
        [
            sg.HSeperator()
        ],
        [
            sg.Text("Select Options", justification='c')
        ],
        [
            sg.HSeperator()
        ],
        get_server_radio(),
        [
            sg.Checkbox("Convert .dll to .dll.ArkApi", key="convert", enable_events=True),
            sg.Radio("Update Plugins", default=True, group_id="server_opt", key="plugin_opt", enable_events=True),
            sg.Radio("Update Admin List", group_id="server_opt", key="admin_list", enable_events=True)
        ],
        [
            sg.Checkbox("Create Backup Plugins on Update", key="create_backup", enable_events=True, default=True)
        ],
        [
            sg.Button("Backup Now", size=(15, .7), key="backup_now", enable_events=True)
        ],
        [
            sg.HSeperator()
        ],
        [
            sg.Text("Select Folder with Plugins to Copy Over", justification='c')
        ],
        [
            sg.In(default_text=get_folder(), size=(30, 1), enable_events=True, key="-FOLDER-", disabled=True),
            sg.FolderBrowse()
        ],
        [
            sg.HSeperator()
        ],
        [
            sg.Text("Below are files/folders that will be copied", justification='c', key="copy_text")
        ],
        get_server_checkboxes(),
        [
            sg.HSeperator()
        ],
        [
            sg.Text("Paths", justification='c')
        ],
        [
            sg.MultilineOutput(autoscroll=True, key="path_output", enable_events=True,
                               default_text="\n".join(get_paths(0, False)))
        ],
        [
            sg.Text("Output", justification='c')
        ],
        [
            sg.MultilineOutput(autoscroll=True, key="code_output", enable_events=True)
        ],
        [
            sg.HSeperator()
        ],
        [
            sg.Button("Confirm", enable_events=True, key="confirm_button"),
            sg.Button("Exit", enable_events=True, key="exit_button")
        ]
    ]

    window = sg.Window(f"Ark Config Copier v{version}", layout=layout, size=(750, 500))
    while True:
        event, values = window.read(timeout=15000, timeout_key='-REFRESH-')

        if event == sg.WINDOW_CLOSED:
            break
        elif event == "reload":
            subprocess.Popen(["ArkConfigCopier.exe"],
                             executable=f"{os.curdir}\\ArkConfigCopier.exe")
            break
        elif event == "exit_button":
            break
        elif event == "-FOLDER-":
            files = []
            for file in os.listdir(values["-FOLDER-"]):
                if os.path.isdir(values["-FOLDER-"] + "\\" + file):
                    if not values["admin_list"]:
                        files.append(file + " (Folder)")
                else:
                    if values["admin_list"]:
                        if file == "AllowedCheaterSteamIDs.txt":
                            files.append(file)
                    else:
                        if file != "AllowedCheaterSteamIDs.txt":
                            files.append(file)
            window["file_output"].update("\n".join(files))
            with open("config.json", "r") as f:
                data = json.loads(f.read())
            data["folder"] = values["-FOLDER-"]
            with open("config.json", "w") as f:
                json.dump(data, f, indent=2)

        elif "server_radio_" in event:
            true_radio = None
            for i in range(3):
                if values[f"server_radio_{i + 1}"]:
                    true_radio = i
                    break
            if true_radio is None:
                continue
            paths = get_paths(true_radio, values["admin_list"])
            window["path_output"].update("\n".join(paths))

        elif event == "admin_list":
            data = get_data()
            if data["folder"] != "":
                admins = data["admins"]
                admin_list = []
                for [key, value] in admins.items():
                    admin_list.append(f"{key}  |  {value}")
                window["file_output"].update("\n".join(admin_list))
                window["copy_text"].update("Below are SteamIDs that will be updated to AllowedCheaterSteamIDs.txt")
            true_radio = None
            for i in range(3):
                if values[f"server_radio_{i + 1}"]:
                    true_radio = i
                    break
            if true_radio is None:
                continue
            window["path_output"].update("\n".join(get_paths(true_radio, True)))

        elif event == "plugin_opt":
            if data["folder"] != "":
                files = []
                for x in os.listdir(data["folder"]):
                    if x != "AllowedCheaterSteamIDs.txt":
                        if os.path.isdir(data["folder"] + "\\" + x):
                            files.append(x + " (Folder)")
                        else:
                            files.append(x)
                window["file_output"].update("\n".join(files))
                window["copy_text"].update("Below are files/folders that will be copied")
            true_radio = None
            for i in range(3):
                if values[f"server_radio_{i + 1}"]:
                    true_radio = i
                    break
            if true_radio is None:
                continue
            window["path_output"].update("\n".join(get_paths(true_radio, False)))

        elif event == "-REFRESH-":
            with open("config.json", "r") as file:
                data = json.loads(file.read())
            if data["folder"] != "":
                files = []
                for file in os.listdir(data["folder"]):
                    if os.path.isdir(data["folder"] + "\\" + file):
                        if not values["admin_list"]:
                            files.append(file + " (Folder)")
                    else:
                        if values["admin_list"]:
                            if file == "AllowedCheaterSteamIDs.txt":
                                files.append(file)
                        else:
                            if file != "AllowedCheaterSteamIDs.txt":
                                files.append(file)

                window["file_output"].update("\n".join(files))

        elif event == "config_options":
            config_window()
            sg.PopupQuickMessage(
                "If changes were made to clusters or directories you must press reload for them to take effect!",
                background_color='grey')

        elif event == "backup_now":
            true_radio = None
            for i in range(3):
                try:
                    if values[f"server_radio_{i + 1}"]:
                        true_radio = i
                        break
                except KeyError:
                    continue
            if true_radio is None:
                continue
            server_names = []
            for key in data["servers"]:
                server_names.append(key)
            output = ["Creating backups..."]
            window["code_output"].update("\n".join(output))
            window.refresh()
            create_backups(get_paths(true_radio, values["admin_list"]),
                           values["-FOLDER-"], server_names[true_radio], values["admin_list"])


        elif event == "confirm_button":
            admin_list = False
            data = get_data()
            if values["-FOLDER-"] == "Select folder where plugins will be pre-loaded":
                continue
            true_radio = None
            for i in range(3):
                try:
                    if values[f"server_radio_{i + 1}"]:
                        true_radio = i
                        break
                except KeyError:
                    continue
            if true_radio is None:
                continue
            server_names = []
            for key in data["servers"]:
                server_names.append(key)
            cluster = data["servers"][server_names[true_radio]]["location"]
            output = [cluster]
            window["code_output"].update("\n".join(output))
            if values["create_backup"]:
                output.append("Creating backups...")
                window["code_output"].update("\n".join(output))
                window.refresh()
                create_backups(get_paths(true_radio, values["admin_list"]),
                               values["-FOLDER-"], server_names[true_radio], values["admin_list"])
            if values["admin_list"]:
                admin_list = True
                pid = None
                output.append("Shutting down ASM...")
                window["code_output"].update("\n".join(output))
                window.refresh()
                while True:
                    for proc in psutil.process_iter():
                        if "Server Manager" in proc.name():
                            pid = proc.pid
                    if pid is not None:
                        p = psutil.Process(pid)
                        p.terminate()
                        pid = None
                    else:
                        break
            if values["convert"]:
                output.append("Searching for .dll files to replace...")
                window["code_output"].update("\n".join(output))
                window.refresh()
                replace_dll(values["-FOLDER-"])
                sleep(2)
            if admin_list:
                admins = data["admins"]
                with open(f"{values['-FOLDER-']}/AllowedCheaterSteamIDs.txt", "w") as file:
                    file.write("\n".join(admins))
            for server in os.listdir(cluster):
                if admin_list:
                    map_path = f"{cluster}\\{server}\\ShooterGame\\Saved"
                else:
                    map_path = f"{cluster}\\{server}\\ShooterGame\\Binaries\\Win64\\ArkApi\\Plugins"
                for file in os.listdir(data["folder"]):
                    if admin_list:
                        if file != "AllowedCheaterSteamIDs.txt":
                            output.append(f"{file} is an invalid Admin List file name... Skipping")
                            window["code_output"].update("\n".join(output))
                            continue
                    else:
                        if file == "AllowedCheaterSteamIDs.txt":
                            continue
                    window["code_output"].update("\n".join(output))
                    recursive_file_move(os.path.join(data["folder"], file), map_path)
                    if admin_list:
                        if file != "AllowedCheaterSteamIDs.txt":
                            pass
                        else:
                            output.append(f"Copying {file} to {server}")
                    else:
                        if file == "AllowedCheaterSteamIDs.txt":
                            pass
                        else:
                            if os.path.isdir(os.path.join(data["folder"], file)):
                                output.append(f"Copying Folder and Contents of {file} to {server}")
                            else:
                                output.append(f"Copying {file} to {server}")
                        window["code_output"].update("\n".join(output))
                        window.refresh()
                output.append(f"{server} Copy Complete!")
                window["code_output"].update("\n".join(output))
                window.refresh()
            output.append("File Copy Complete!")
            window["code_output"].update("\n".join(output))
            window.refresh()
            if values["admin_list"]:
                output.append("Re-opening ASM...")
                window["code_output"].update("\n".join(output))
                window.refresh()
                subprocess.Popen(["ARK Server Manger.exe"],
                                 executable="C:\\Program Files\\ArkServerManager\\ARK Server Manager.exe")

    window.close()


main()
