from threading import Thread, Event
from gevent.pywsgi import WSGIServer
import os
from server import app
from data import db
import atexit
import shelve
import datetime
import httpagentparser
import colorama
from utils import (
    exit_handler,
    watcher,
    clear,
    invalid,
    cursor,
    help_message,
    info,
    play_audio,
)



colorama.init()
colors = [
    colorama.Fore.LIGHTBLUE_EX,
    colorama.Fore.GREEN,
    colorama.Fore.LIGHTCYAN_EX,
]
threads = []

# on program end
atexit.register(exit_handler)

# on program start
with shelve.open('saved/state') as state:
    if {"status", "datetime"} <= state.keys():
        db.internal_data["status"] = state["status"]
        if state["status"] == "work":
            play_audio()
            db.internal_data["datetime"] = datetime.datetime.now()
        else:
            db.internal_data["datetime"] = state["datetime"]


def main():
    clear()
    while True:
        cursor()
        x = input()
        if x.lower() == 'exit':
            clear()
            exit_handler()
            os._exit(1)
            break
        options(x)


def set_command(options=[]):
    if len(options) <= 1:
        print("\nError: there must be over 2 set args\n")
    elif options[0] == "command":
        db.data["command"] = options[1]


def set_status(options=[]):
    current = db.internal_data["status"]
    statuses = db.config["breaks"].keys()
    if options[0] not in statuses or len(options) < 1:
        print("\nInvalid status, list of statuses:")
        for i in statuses:
            print(
                "{blue}-{green} {stat}".format(blue=colors[0], green=colors[1], stat=i)
            )
        print(colors[2])
    elif db.config["breaks"][options[0]]["limit"] < 1:
        print(
            "\n{blue}{stat}{normal} limit reached {green}0{normal}, you are not allowed \n".format(
                stat=options[0], blue=colors[0], green=colors[1], normal=colors[2]
            )
        )
    elif current == options[0]:
        print("your current status is already: " + current + "\n")
    else:
        db.internal_data["datetime"] = datetime.datetime.now()
        db.internal_data["status"] = options[0]
        db.config["breaks"][options[0]]["limit"] -= 1
        print("\nstatus set to: " + colors[0] + options[0] + colors[2])
        print(
            "new-limit: {green}{limit}{normal}, time: {green}{time}{normal} minutes\n".format(
                limit=db.config["breaks"][options[0]]["limit"],
                time=db.config["breaks"][options[0]]["minutes"],
                green=colors[1],
                normal=colors[2],
            )
        )


def get_clients(options=[]):
    uas = db.internal_data["userAgents"]
    print(
        "\n{green}Info:{normal} you have {blue}{n}{normal} client connected\n".format(
            green=colors[1], normal=colors[2], blue=colors[0], n=len(uas)
        )
    )
    for i in range(0, len(uas)):
        info = httpagentparser.simple_detect(uas[i])
        print(
            "{blue}{num}{normal}: [{green}{os}{normal}] {blue}{browser}{normal}".format(
                num=i + 1,
                os=info[0],
                browser=info[1],
                green=colors[1],
                normal=colors[2],
                blue=colors[0],
            )
        )
    print()


def options(op):
    options = op.split()
    option = options[0]
    switcher = {
        "clear": clear,
        "set": set_status,
        "clients": get_clients,
        "help": help_message,
        "info": info,
    }
    try:
        switcher.get(option.lower(), invalid)(options[1:])
    except Exception as e:
        invalid()
        print(e)


if __name__ == "__main__":
    try:
        # running the main and watcher loops in different threads
        # so they don't interfere with our web server
        Thread(target=main, daemon=True).start()
        Thread(target=watcher, daemon=True).start()
        
        # server in production mode with gevent
        http_server = WSGIServer(
            (db.config["host"], db.config["port"]), app, log=app.logger
        )
        http_server.serve_forever()
    except KeyboardInterrupt:
        # definitely not doing this to hide errors or anything
        clear()