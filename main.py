import PySimpleGUIQt as sg
import datetime
import json
import time
from datetime import datetime


def main():
    with open("config.json", "r") as file:
        data = json.loads(file.read())
        print(data["25xpve"].items())

    layout = [
        [
            sg.Radio()
        ]
    ]

    window = sg.Window(f"Test Window", layout=layout)
    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED:
            break
    window.close()


main()
