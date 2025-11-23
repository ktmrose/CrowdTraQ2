import json, sys
from unittest.mock import patch, MagicMock
import app.admin as admin


# --- authorize() ---
@patch("app.admin.SpotifyConnectionManager")
def test_authorize_prints_url(mock_mgr, capsys):
    mock_conn = MagicMock()
    mock_conn.get_authorization_url.return_value = "http://fake-url"
    mock_mgr.get_instance.return_value = mock_conn

    admin.authorize()
    out = capsys.readouterr().out
    assert "http://fake-url" in out
    assert "Go to this URL" in out


# --- refresh() ---
@patch("app.admin.SpotifyConnectionManager")
def test_refresh_with_tokens_file(mock_mgr, tmp_path, capsys):
    token_info = {"access_token": "abc", "refresh_token": "def", "expires_at": 123}
    tokens_file = tmp_path / "tokens.json"
    tokens_file.write_text(json.dumps(token_info))
    admin.TOKENS_FILE = str(tokens_file)

    mock_conn = MagicMock()
    mock_mgr.get_instance.return_value = mock_conn

    admin.refresh()
    out = capsys.readouterr().out
    assert "Tokens refreshed and saved." in out
    mock_conn.load_token_info.assert_called_once_with(token_info)
    assert mock_conn.refresh_access_token.called
    assert mock_conn.save_tokens.called


@patch("app.admin.SpotifyConnectionManager")
def test_refresh_without_tokens_file(mock_mgr, tmp_path, capsys):
    admin.TOKENS_FILE = str(tmp_path / "tokens.json")
    mock_conn = MagicMock()
    mock_mgr.get_instance.return_value = mock_conn

    admin.refresh()
    out = capsys.readouterr().out
    assert "No tokens.json found" in out
    mock_conn.load_token_info.assert_not_called()


# --- status() ---
def test_status_prints_token_info(tmp_path, capsys):
    token_info = {"access_token": "abc", "refresh_token": "def"}
    tokens_file = tmp_path / "tokens.json"
    tokens_file.write_text(json.dumps(token_info))
    admin.TOKENS_FILE = str(tokens_file)

    admin.status()
    out = capsys.readouterr().out
    assert "Current token info:" in out
    assert '"access_token": "abc"' in out


def test_status_without_tokens_file(tmp_path, capsys):
    admin.TOKENS_FILE = str(tmp_path / "tokens.json")
    admin.status()
    out = capsys.readouterr().out
    assert "No tokens.json found" in out


# --- main() ---
def test_main_authorize_branch(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["admin.py", "authorize"])
    with patch.object(admin, "authorize") as mock_auth:
        admin.main()
        mock_auth.assert_called_once()

def test_main_refresh_branch(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["admin.py", "refresh"])
    with patch.object(admin, "refresh") as mock_refresh:
        admin.main()
        mock_refresh.assert_called_once()

def test_main_status_branch(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["admin.py", "status"])
    with patch.object(admin, "status") as mock_status:
        admin.main()
        mock_status.assert_called_once()