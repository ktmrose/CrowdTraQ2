from flask import request, jsonify, Blueprint
from spotify import SpotifyConnection

spotify_bp = Blueprint('spotify', __name__)
spotify_connection = SpotifyConnection()

def register_routes(app):
    app.register_blueprint(spotify_bp)

@spotify_bp.route("/callback")
def callback():
    authorization_code = request.args.get("code")
    if not authorization_code:
        return "Error: Missing authorization code", 400

    token_info = spotify_connection.exchange_code_for_token(authorization_code)
    print("user granted permission")
    return jsonify(token_info)  # For now, just display the tokens