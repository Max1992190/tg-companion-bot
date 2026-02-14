import json
import os
import time
from src.config import DATA_FILE


def _ensure_data_dir():
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)


def _load_all() -> dict:
    _ensure_data_dir()
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def _save_all(data: dict):
    _ensure_data_dir()
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_user(user_id: int) -> dict:
    data = _load_all()
    uid = str(user_id)
    if uid not in data:
        data[uid] = _default_user()
        _save_all(data)
    return data[uid]


def save_user(user_id: int, user_data: dict):
    data = _load_all()
    data[str(user_id)] = user_data
    _save_all(data)


def _default_user() -> dict:
    return {
        "age_confirmed": False,
        "blocked": False,
        "name": None,
        "state": "new",
        "current_companion": None,
        "companions_used": [],
        "companion_data": {},
        "mood": "warm",
        "mood_last_change": time.time(),
        "last_emoji": None,
        "bonus_given": False,
        "last_paid_ended_at": 0,
    }


def get_companion_data(user: dict, companion_id: str) -> dict:
    if companion_id not in user.get("companion_data", {}):
        user.setdefault("companion_data", {})[companion_id] = {
            "free_ai_count": 0,
            "paywall_shown": False,
            "paid_until": 0,
            "bonus_given": False,
            "paid_ended_at": 0,
            "photos_sent": [],
            "last_photo_time": 0,
            "chat_history": [],
            "minute_warning_shown": False,
        }
    return user["companion_data"][companion_id]
