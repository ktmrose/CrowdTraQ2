from flask import Flask, request, jsonify
from spotify import SpotifyConnection

app = Flask(__name__)

spotify_connection = SpotifyConnection()

@app.route("/callback")
def callback():
    authorization_code = request.args.get("code")
    if not authorization_code:
        return "Error: Missing authorization code", 400

    token_info = spotify_connection.exchange_code_for_token(authorization_code)
    print("user granted permission")
    return jsonify(token_info)  # For now, just display the tokens