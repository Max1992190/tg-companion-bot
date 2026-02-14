import os

LOG_FILE = "data/dialog_logs.txt"
MAX_ENTRIES = 100
SEPARATOR = "-----\n"


def _ensure_dir():
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)


def log_dialog(user_text: str, bot_text: str):
    _ensure_dir()
    entry = f"USER: {user_text}\nBOT: {bot_text}\n{SEPARATOR}"

    entries = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        if content.strip():
            entries = [e + SEPARATOR for e in content.split(SEPARATOR) if e.strip()]

    entries.append(entry)
    if len(entries) > MAX_ENTRIES:
        entries = entries[-MAX_ENTRIES:]

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("".join(entries))


def get_last_dialogs(count: int = 10) -> str:
    if not os.path.exists(LOG_FILE):
        return ""
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    if not content.strip():
        return ""
    entries = [e.strip() for e in content.split(SEPARATOR) if e.strip()]
    last = entries[-count:]
    return ("\n" + SEPARATOR).join(last)
