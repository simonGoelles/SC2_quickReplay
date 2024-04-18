import pytest
from unittest.mock import patch, MagicMock
from main import app

# another sample player data for testing here
PLAYER_DATA = {
    "name": "Player1",
    "race": "Protoss",
    "apm": 150,
    "result": "Win"
}


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_file_upload_success(client):
    # Prepare a mock file for upload
    mock_file = MagicMock()
    mock_file.filename = "test_replay.SC2Replay"

    # Make a request to the upload endpoint with the mock file
    response = client.post('/upload', data={'file': mock_file})

    assert response.status_code == 200 # 200 heist ok

    assert b"File uploaded successfully" in response.data


def test_player_information(client):
    # Mock read_replay to return sample player data
    with patch('main.read_replay', return_value={"players": [PLAYER_DATA]}):
        # Make a request to the get_player_info endpoint
        response = client.get('/get_player_info')

    assert response.status_code == 200

    assert response.json == PLAYER_DATA


def test_html_rendering(client):
    # Make a request to the index endpoint
    response = client.get('/')

    assert response.status_code == 200

    assert b"<title>StarCraft 2 Replay Viewer</title>" in response.data
    assert b"<h2>Welcome to StarCraft 2 Replay Viewer</h2>" in response.data
