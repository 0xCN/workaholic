"""
This class acts as a state container by making a 'db' object and
importing it to other files, not ideal.. but gets the job done
"""

import os, json, datetime


class Data:
    platform = os.name
    data = {"connection": "ping", "command": "none"}
    config = json.load(open("chrome-extension/config.json", "r"))
    internal_data = {
        "userAgents": [],
        "status": "chillin",
        "datetime": datetime.datetime.now()
    }
    # yes, this is what i sound like (deep sexy demon)
    audio = {
        "distraction": ["close_tab.mp3", "remove_distractions.mp3", "you_will_pay.mp3"],
        "idle": ["back_to_work.mp3", "why.mp3"],
        "time": ["back_to_work.mp3", "you_are_late.mp3"],
        "suffer": ["EAS.mp3"]
    }
    # TODO: find more annoying audio files for the "suffer" category


db = Data()