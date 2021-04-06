import os
import time
from data import db
from ctypes import Structure, windll, c_uint, sizeof, byref
from playsound import playsound
import random
import datetime
import shelve
import colorama


colorama.init()
colors = [
    colorama.Fore.LIGHTBLUE_EX,
    colorama.Fore.GREEN,
    colorama.Fore.LIGHTCYAN_EX,
]
help_str = """
            {blue}Help Message{normal}

- {green}help{normal}: show this message
- {green}clients{normal}: show connected browser extensions
- {green}clear{normal}: clear the screen
- {green}set{normal}: set status, syntax: $: set {blue}[status]{normal}
- {green}info{normal}: show current states
- {green}exit{normal}: exit the program

# do {blue}info{normal} to see list of statuses
# failure to get back on time and set mode to work will cause sounds to go off
# you can configure time limits at {green}'chrome-extension/config.json'{normal}

""".format(
    break_minutes=db.config["breaks"]["break"]["minutes"],
    break_limit=db.config["breaks"]["break"]["limit"],
    eating_minutes=db.config["breaks"]["eating"]["minutes"],
    eating_limit=db.config["breaks"]["eating"]["limit"],
    study_minutes=db.config["breaks"]["studying"]["minutes"],
    study_limit=db.config["breaks"]["studying"]["limit"],
    chores_minutes=db.config["breaks"]["chores"]["minutes"],
    chores_limit=db.config["breaks"]["chores"]["limit"],
    bathroom_minutes=db.config["breaks"]["bathroom"]["minutes"],
    bathroom_limit=db.config["breaks"]["bathroom"]["limit"],
    sleep_time=db.config["breaks"]["sleep"]["minutes"] / 60.0,
    blue=colors[0], green=colors[1], normal=colors[2]
)


def help_message(options=[]):
    print(help_str)


def exit_handler():
    if db.internal_data["status"] == "work":
        print("[SUFFER] ENDED BEFORE GOING TO SLEEP")
        play_audio()
    print("- program ended, saving states", end="")
    with shelve.open("saved/state") as state:
        print(".", end="")
        state["status"] = db.internal_data["status"]
        print(".", end="")
        state["datetime"] = db.internal_data["datetime"]
        print(".")
    print("- states saved"+colors[2])


def cursor():
    print(colorama.Fore.RED + "$" + colorama.Fore.LIGHTCYAN_EX + ": ", end="")


def print_banner():
    print("  " + colorama.Fore.LIGHTCYAN_EX + ",")
    print(
        "{coffee}c[_]    {workaholic}--=Workaholic=--    {version}{v}\n{n}".format(
            coffee=colorama.Fore.LIGHTBLUE_EX,
            workaholic=colorama.Fore.LIGHTGREEN_EX,
            version=colorama.Fore.LIGHTBLUE_EX,
            v=db.config["version"],
            n=colorama.Fore.LIGHTCYAN_EX
        )
    )


def clear(options=[]):
    if db.platform == "nt":
        os.system("cls")
    else:
        os.system("clear")
    print_banner()


def invalid(options=[]):
    print("Error: invalid command\n")


def info(options=[]):
    colors = [
        colorama.Fore.LIGHTBLUE_EX,
        colorama.Fore.GREEN,
        colorama.Fore.LIGHTCYAN_EX,
    ]

    current = db.internal_data["status"]
    start_time = db.internal_data["datetime"].strftime("%m/%d/%Y, %H:%M:%S")
    clients = len(db.internal_data["userAgents"])
    stats = db.config["breaks"]
    idle = db.config["idle_limit"] / 60.0
    blocked = db.config["blocked_domains"]
    process = db.config["process"]
    blocked_str = "["
    for i in range(len(blocked)):
        blocked_str += colors[1] + '"' + blocked[i] + '"' + colors[2]
        if i != len(blocked) - 1:
            blocked_str += ", "
    blocked_str += "]"
    server = (
        colors[1]
        + "http://"
        + db.config["host"]
        + colors[1]
        + ":"
        + colors[0]
        + str(db.config["port"])
        + colors[1]
        + "/"
        + colors[2]
    )

    print(
        "\nstatus: {}, start-time: {}\nconnected-clients: {}, idle-time-limit: {} minutes".format(
            colors[0] + current + colors[2],
            colors[1] + start_time + colors[2],
            colors[1] + str(clients) + colors[2],
            colors[1] + str(idle) + colors[2],
        )
    )
    print("process-to-be-monitored: {}".format(colors[0] + process + colors[2]))
    print("blocked-domains: {}".format(blocked_str))
    print("web-server: {}\n".format(server))
    for i in stats:
        print(
            "{:<18} | {}{:<19}|  {}{}".format(
                colors[0] + i + colors[2],
                "time: ",
                colors[1] + str(stats[i]["minutes"]) + colors[2],
                "limit: ",
                colors[1] + str(stats[i]["limit"]) + colors[2],
            )
        )
    print("\n{:>8}[time is in minutes] \n".format(""))


def get_task():
    name = db.config["process"]
    check = os.popen('tasklist /FI "IMAGENAME eq {}"'.format(name)).read().strip()[0:4]
    if check.lower() == "info":
        return True
    else:
        return False


class LASTINPUTINFO(Structure):
    _fields_ = [
        ("cbSize", c_uint),
        ("dwTime", c_uint),
    ]


def get_idle_duration():
    lastInputInfo = LASTINPUTINFO()
    lastInputInfo.cbSize = sizeof(lastInputInfo)
    windll.user32.GetLastInputInfo(byref(lastInputInfo))
    millis = windll.kernel32.GetTickCount() - lastInputInfo.dwTime
    return millis / 1000.0


def play_audio(type="suffer"):
    file_name = random.choice(db.audio[type])
    path = "audio/{type}/{file_name}".format(type=type, file_name=file_name)
    playsound(path)


def watcher():
    i = 0
    n = 0
    while True:
        status = db.internal_data["status"]
        if status == "work":
            idle = get_idle_duration()
            i += 1
            if i % 5 == 0 and get_task():
                play_audio("idle")
                i = 0
            elif idle > db.config["idle_limit"]:
                play_audio("idle")
                play_audio("suffer")
                db.internal_data["status"] = "idle"
                i = 0

        elif status == "idle":
            idle = get_idle_duration()
            # when user gets back
            if idle < 2:
                play_audio("idle")
                play_audio("suffer")
                db.internal_data["status"] = "work"

        elif status in db.config["breaks"].keys():
            date = db.internal_data["datetime"]
            now = datetime.datetime.now()
            difference = now - date
            difference = difference.total_seconds()
            if difference > db.config["breaks"][status]["minutes"] * 60:
                if get_idle_duration() < 2:
                    play_audio("time")
                    # mental torture
                    play_audio("suffer")
                    db.internal_data["status"] = "work"
            time.sleep(5)

        elif n > 60:
            # emptying list of user-agents
            # this helps keep track of connected clients
            db.internal_data["userAgents"] = []
            n = 0

        n += 1
        time.sleep(1)