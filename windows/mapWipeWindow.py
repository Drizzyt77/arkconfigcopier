from cgitb import enable
import datetime
import json
import math
import os
import shutil
import threading
from time import sleep
from tkinter import E
import zipfile
import PySimpleGUIQt as sg

from utils import get_data


def get_clusters():
    data = get_data()
    clusters = []
    for x in data["servers"]:
        clusters.append(x)
    return clusters

def get_maps(cluster):
    data = get_data()
    cluster = data["servers"][cluster]["location"]
    maps = []
    for x in os.listdir(cluster):
        maps.append(x)
    return maps

def get_asm(folder):
    if not os.path.exists(folder + '/clusters'):
        return []
    else:
        items = os.listdir(folder + '/clusters')
        return items

def get_asm_dir():
    data = get_data()
    return data["asm_folder"]

class Fake_logger:
    def __init__(self):
        self.path = ''

    def info(self, s, *args):
        if args:
            self.path = args[0]

    def debug(self, s, *args):
        pass

def folder_size(folder_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return total_size

def get_layout():
    layout = [
        [
            sg.Text("Wipe Maps", justification='c')
        ],
        [
        sg.HSeperator()
        ],
        [
        sg.Text("Select ASM Data Folder", justification='c')
        ],
        [
        sg.In(get_asm_dir(), disabled=True, key="asm_folder", enable_events=True),
        sg.FolderBrowse()
        ],
        [
        sg.HSeperator()
        ],
        [
        sg.Listbox(values=get_asm(get_asm_dir()), key="asm_cluster")
        ],
        [
        sg.Button("Select ASM Data Cluster", key="asm_button", enable_events=True)
        ],
        [
        sg.In(disabled=True, key="asm_select")
        ],
        [
        sg.HSeperator()  
        ],
        [
        sg.Text("Select a Cluster to Wipe", justification='c')
        ],
        [
        sg.Listbox(get_clusters(), enable_events=True, key="clusters")
        ],
        [
        sg.Listbox(values=[], key="maps", disabled=True)
        ],
        [
        sg.Button("Wipe All Maps", enable_events=True, key="wipe")
        ],
        [
        sg.HSeperator()
        ],
        [
        sg.Text("Output", justification='c')
        ],
        [
        sg.MultilineOutput(key="output", autoscroll=True, size=(750, 200))
        ],
        [
            sg.Button("Close", enable_events=True, key="close")
        ]
    ]
    return layout


def wipeWindow():
    window = sg.Window("Wipe Control Panel", layout=get_layout(), size=(750, 200))
    while True:
        event, values = window.read()
        
        if event == sg.WINDOW_CLOSED or event == "close":
            window.close()
            break
        elif event == "clusters":
            window["maps"].update(get_maps(values["clusters"][0]))
        elif event == "asm_folder":
            window["asm_cluster"].update(values=get_asm(values["asm_folder"]))
            data = get_data()
            data["asm_folder"] = values["asm_folder"]
            with open("config.json", "w") as file:
                json.dump(data, file, indent=2)
        elif event == "asm_button":
            if values["asm_cluster"] == []:
                continue
            window["asm_select"].update(values["asm_cluster"][0])
        elif event == "wipe":
            if values["clusters"] == []:
                continue
            denied = ["Config", "Logs", "SaveGames", "AllowedCheaterSteamIDs.txt"]
            data = get_data()
            path = data["servers"][values['clusters'][0]]["location"]
            add_path = 'ShooterGame\Saved'
            output = []
            default_dir = os.getcwd()
            try:
                maps = get_maps(values["clusters"][0])
                for m in maps:
                    output.append(f"Beginning wipe of {m}...")
                    window["output"].update("\n".join(output))
                    window.refresh()
                    sleep(2)
                    new_path = os.path.join(os.path.join(path, m), add_path)
                    for f in os.listdir(new_path):
                        if f not in denied:
                            if zipfile.is_zipfile(os.path.join(new_path, f)):
                                continue
                            if folder_size(os.path.join(new_path, f)) == 0:
                                continue
                            output.append(f"Creating backup for {m}...")
                            window["output"].update("\n".join(output))
                            window.refresh()
                            sleep(1)
                            try:
                                os.chdir(new_path)
                                now = datetime.datetime.now()
                                now = now.strftime("%m-%d-%y--%I;%M%p")
                                logger = Fake_logger()
                                zipThread = threading.Thread(target= shutil.make_archive, args= (f'{f}-{now}.backup', 'zip', os.path.join(new_path, f)), kwargs = {'logger':logger})
                                zipThread.start()

                                Last_path = logger.path
                                allsize = folder_size(os.path.join(new_path, f))
                                size = 0
                                output.append(f"Backup Progress: 0%")
                                sg.OneLineProgressMeter('Progress', 0, 100, 'progress', 'Creating Backup Zip', orientation='horizontal', bar_color=['Green', 'Red'])
                                while zipThread.is_alive():
                                    if logger.path != Last_path:
                                        if os.path.isfile(os.path.join(new_path, f)+'\\'+Last_path):
                                            size+= os.path.getsize(os.path.join(new_path, f)+'\\'+Last_path)
                                        Last_path = logger.path
                                        if output[-1] == "Backup Progress 0%":
                                            pass
                                        else:
                                            del output[-1]
                                        try:
                                            out_size = math.floor(size/allsize*100)
                                        except ZeroDivisionError:
                                            out_size = 100
                                        output.append(f"Backup Progress: {out_size}%")
                                        window["output"].update("\n".join(output))
                                        sg.OneLineProgressMeter('Progress', out_size, 100, 'progress', 'Creating Backup Zip', orientation='horizontal', bar_color=['Green', 'Red'])
                                        window.refresh()
                                    else:
                                        sleep(.005)
                                del output[-1]
                                output.append(f"Backup Progress: 100%")
                                window["output"].update("\n".join(output))
                                sg.OneLineProgressMeter('Progress', 100, 100, 'progress', 'Creating Backup Zip', orientation='horizontal', bar_color=['Green', 'Red'])
                                window.refresh()
                                output.append(f"Backup Created for {m}...")
                                window["output"].update("\n".join(output))
                                window.refresh()
                                sleep(1)
                            except Exception as e:
                                output.append(f"Creating backup for {m} failed with Error: {e}")
                                window["output"].update("\n".join(output))
                                out_size = 0
                                window.refresh()
                                sleep(1)
                            prog = 0
                            max_prog = len(os.listdir(os.path.join(new_path, f)))
                            print(max_prog)
                            if max_prog != 0:
                                sg.OneLineProgressMeter('Progress', prog, max_prog, 'progress', 'Wiping Files...', orientation='horizontal', bar_color=['Green', 'Red'])
                            for x in os.listdir(os.path.join(new_path, f)):
                                os.remove(os.path.join(os.path.join(new_path, f), x))
                                prog += 1
                                output.append(f"Wiping file {x}")
                                window["output"].update("\n".join(output))
                                if max_prog != 0:
                                    sg.OneLineProgressMeter('Progress', prog, max_prog, 'progress', 'Wiping Files...', orientation='horizontal', bar_color=['Green', 'Red'])
                                window.refresh()
                                sleep(.01)
                            os.chdir(default_dir)
                    output.append(f"Completed wipe of {m}...")
                    window["output"].update("\n".join(output))
                    window.refresh()
                output.append("Beginning wipe of ASM Data...")
                window["output"].update("\n".join(output))
                window.refresh()
                if data["asm_folder"] != '':
                    if values["asm_select"] != '':
                        path = data["asm_folder"] + f"/clusters/{values['asm_select']}"
                        prog = 0
                        max_prog = len(os.listdir(path))
                        if max_prog != 0:
                            sg.OneLineProgressMeter('Progress', prog, max_prog, 'progress', 'Wiping ASM Data...', orientation='horizontal', bar_color=['Green', 'Red'])
                        for x in os.listdir(path):
                            prog += 1
                            os.remove(os.path.join(path, x))
                            output.append(f"Wiping Player File {x}...")
                            window["output"].update("\n".join(output))
                            if max_prog != 0:
                                sg.OneLineProgressMeter('Progress', prog, max_prog, 'progress', 'Wiping ASM Data...', orientation='horizontal', bar_color=['Green', 'Red'])
                            window.refresh()
                        output.append("Completed ASM Data Wipe...")
                        window["output"].update("\n".join(output))
                        window.refresh()
                        
                    else:
                        output.append("ASM Cluster Not Selected...")
                        window["output"].update("\n".join(output))
                        window.refresh()
                else:
                    output.append("ASM Data Folder Not Selected...")
                    window["output"].update("\n".join(output))
                    window.refresh()
                output.append("All Wipes Completed...")
                window["output"].update("\n".join(output))
                window.refresh()
                            

            except IndexError:
                print("Error")
            