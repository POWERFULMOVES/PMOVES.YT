from fastapi.testclient import TestClient

from pmoves_yt_service import yt as app_module


def test_playlist_add_returns_preview_by_default(monkeypatch):
    events = []
    monkeypatch.setattr(app_module, '_publish_event', lambda topic, payload: events.append((topic, payload)))

    client = TestClient(app_module.app)
    resp = client.post(
        '/yt/control/playlist/add',
        json={
            'playlist_id': 'PL123',
            'video_id': 'vid-123',
        },
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data['status'] == 'preview'
    assert data['action'] == 'playlist_add'
    assert data['details']['playlist_id'] == 'PL123'
    assert events[0][0] == 'creator.youtube.control.preview.v1'


def test_playlist_add_execute_requires_approval(monkeypatch):
    monkeypatch.setattr(app_module, 'YT_CONTROL_REQUIRE_APPROVAL', True)

    client = TestClient(app_module.app)
    resp = client.post(
        '/yt/control/playlist/add',
        json={
            'playlist_id': 'PL123',
            'video_id': 'vid-123',
            'execute': True,
        },
    )

    assert resp.status_code == 400
    assert resp.json()['detail'] == 'approved_by is required when execute=true'


def test_comment_execute_uses_youtube_control_runtime(monkeypatch):
    events = []
    monkeypatch.setattr(app_module, '_publish_event', lambda topic, payload: events.append((topic, payload)))
    monkeypatch.setattr(app_module, 'YT_GOOGLE_CLIENT_ID', 'client-id')
    monkeypatch.setattr(app_module, 'YT_GOOGLE_CLIENT_SECRET', 'client-secret')
    monkeypatch.setattr(app_module, 'YT_GOOGLE_REFRESH_TOKEN', 'refresh-token')
    monkeypatch.setattr(app_module, 'YT_CONTROL_REQUIRE_APPROVAL', True)
    monkeypatch.setattr(app_module, 'refresh_access_token', lambda **kwargs: 'access-token')
    monkeypatch.setattr(
        app_module,
        'insert_comment',
        lambda **kwargs: {'id': 'comment-1', 'snippet': {'videoId': kwargs['video_id']}},
    )

    client = TestClient(app_module.app)
    resp = client.post(
        '/yt/control/comment',
        json={
            'video_id': 'vid-123',
            'text': 'Thanks for the video',
            'execute': True,
            'approved_by': 'discord-agent',
            'approval_note': 'networking follow-up',
        },
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data['status'] == 'executed'
    assert data['action'] == 'comment_create'
    assert data['result']['id'] == 'comment-1'
    assert events[0][0] == 'creator.youtube.control.executed.v1'
