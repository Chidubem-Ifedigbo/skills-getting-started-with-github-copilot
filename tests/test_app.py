import os
import sys

# Ensure repository root is on sys.path so `src` package can be imported
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from fastapi.testclient import TestClient
from src.app import app


client = TestClient(app)


def get_participants(activity_name):
    data = client.get('/activities').json()
    return data[activity_name]['participants']


def test_get_activities():
    resp = client.get('/activities')
    assert resp.status_code == 200
    data = resp.json()
    # Expect several activities defined
    assert 'Chess Club' in data
    assert isinstance(data['Chess Club']['participants'], list)


def test_signup_and_unregister_cycle():
    activity = 'Chess Club'
    email = 'test.user@example.com'

    # Ensure email not already present
    participants_before = get_participants(activity)
    if email in participants_before:
        # remove before testing to ensure determinism
        client.delete(f"/activities/{activity}/participants?email={email}")

    # Sign up
    signup_resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert signup_resp.status_code == 200
    assert 'Signed up' in signup_resp.json().get('message', '')

    # Check participant was added
    participants_after = get_participants(activity)
    assert email in participants_after

    # Unregister
    del_resp = client.delete(f"/activities/{activity}/participants?email={email}")
    assert del_resp.status_code == 200
    assert 'Unregistered' in del_resp.json().get('message', '')

    # Final check: removed
    participants_final = get_participants(activity)
    assert email not in participants_final
