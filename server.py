from data import db
from flask import request, jsonify, Flask, request
from utils import play_audio

app = Flask(__name__)


@app.route("/", methods=["GET"])
def main():
    ua = request.headers.get("User-Agent")
    if ua in db.internal_data["userAgents"]:
        pass
    else:
        db.internal_data["userAgents"].append(ua)

    db.data["status"] = db.internal_data["status"]
    return jsonify(db.data)


@app.route("/bad-tab", methods=["GET"])
def tab():
    play_audio('distraction')
    play_audio()
    return jsonify(db.data)