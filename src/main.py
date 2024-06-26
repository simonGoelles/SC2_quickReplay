from flask import Flask, render_template, request, jsonify
import sc2reader
from sc2reader.engine.plugins import APMTracker, SelectionTracker
import os
import datetime
import re

sc2reader.engine.register_plugin(APMTracker())

app = Flask(__name__)

uploads_dir = os.path.join(app.static_folder, 'uploads')
os.makedirs(uploads_dir, exist_ok=True)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_player_info')
def get_player_info():
    # Mocked player data for testing
    player_data = {
        "name": "Player1",
        "race": "Protoss",
        "apm": 150,
        "result": "Win"
    }

    return jsonify(player_data)


@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return "No file part"

    file = request.files['file']

    if file.filename == '':
        return "No selected file"

    replay_path = os.path.join(uploads_dir, file.filename)
    file.save(replay_path)

    replay_info = read_replay(replay_path)
    return render_template('result.html', replay_info=replay_info)


def read_replay(replay_path):
    replay = sc2reader.load_replay(replay_path)

    replay_info = {
        "map_name": replay.map_name,
        "game_length": replay.game_length.seconds,
        "players": []
    }

    for player in replay.players:

        pattern = r"\((.*?)\)"
        difficulty = re.findall(pattern, player.name)

        resources_mined = 0
        resources_lost = 0

        for event in replay.events:
            if isinstance(event, sc2reader.events.tracker.UnitBornEvent):
                if event.control_pid == player.pid:
                    resources_mined += event.unit_value_minerals

            elif isinstance(event, sc2reader.events.tracker.UnitDiedEvent):
                if event.killing_player_id == player.pid:
                    resources_lost += event.unit_value_minerals

        if player.is_human:
            apm = player.avg_apm
        else:
            apm = f"Avg AI {difficulty[0]} APM"

        player_info = {
            "name": player.name,
            "race": player.pick_race,
            "resources mined": resources_mined,
            "resources lost": resources_lost,
            "apm": apm,
            "result": player.result 
        }
        replay_info["players"].append(player_info)

    return replay_info



if __name__ == '__main__':
    app.run(debug=True)
