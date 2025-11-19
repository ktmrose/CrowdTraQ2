from flask import request, Blueprint, after_this_request
from app.services.spotify_manager import SpotifyConnectionManager

spotify_bp = Blueprint('spotify', __name__)

def register_routes(app):
    app.register_blueprint(spotify_bp)

@spotify_bp.route("/callback")
def callback():
    @after_this_request
    def add_header(response):
        response.headers['Connection'] = 'close'
        return response
    authorization_code = request.args.get("code")
    if not authorization_code:
        return "Error: Missing authorization code", 400

    spotify_connection = SpotifyConnectionManager.get_instance()
    spotify_connection.exchange_code_for_token(authorization_code)
    #TODO: make this message prettier and maybe redirect to a different page
    return "Authorization successful! You may now close this window and start the main server"