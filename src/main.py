from flask import Flask, render_template, request
import sc2reader

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return "No file part"

    file = request.files['file']

    if file.filename == '':
        return "No selected file"

    replay_path = f"uploads/{file.filename}"
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
        player_info = {
            "name": player.name,
            "race": player.pick_race,
            "apm": player.apm,
            "result": player.result
        }
        replay_info["players"].append(player_info)

    return replay_info


if __name__ == '__main__':
    app.run(debug=True)
