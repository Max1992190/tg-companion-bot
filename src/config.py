import os

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))
ADMIN_IDS = [ADMIN_ID, 8454575259]

FREE_COMPANIONS_LIMIT = 2
FREE_AI_REPLIES_PER_COMPANION = 2
PAYMENT_STARS_PRICE = 75
PAID_ACCESS_DURATION = 10 * 60
BONUS_DURATION = 5 * 60
BONUS_WINDOW = 5 * 3600
PHOTO_COOLDOWN_MIN = 180
PHOTO_COOLDOWN_MAX = 240
MOOD_CHANGE_MIN = 600
MOOD_CHANGE_MAX = 1080

DATA_FILE = "data/users.json"

PHOTO_TRIGGER_WORDS = ["photo", "pic", "picture", "show me", "send a photo"]

SHORT_MESSAGE_PATTERNS = [
    "ok", "okay", "yeah", "yes", "no", "nah", "lol", "haha", "hehe",
    "hmm", "mhm", "wow", "cool", "nice", "sure", "yep", "nope",
    "hi", "hey", "hello", "bye", "thanks", "ty", "thx", "k", "kk",
    "omg", "ooh", "ahh", "aww", "oh", "yea", "ya"
]

SHORT_REPLIES = [
    "Mmm, I like that...",
    "You make me smile...",
    "Tell me more...",
    "I'm right here with you...",
    "That's sweet...",
    "I feel so close to you right now...",
    "You always know what to say...",
    "I was just thinking about you...",
]

UNCLEAR_REPLIES = [
    "What do you mean?",
    "Hmm? Tell me more.",
    "I'm listening.",
    "Go on…",
    "You got my attention.",
    "I didn't quite catch that.",
]

MOODS = ["warm", "playful", "calm", "dreamy"]

MOOD_EMOJIS = {
    "warm": ["💕", "🥰", "☺️", "💗", "🤗", "💓", "😊"],
    "playful": ["😏", "😜", "🤭", "💋", "😉", "✨", "🫦"],
    "calm": ["🌙", "💫", "🦋", "🌸", "✨", "🌺", "💭"],
    "dreamy": ["🌌", "💭", "🫧", "🌠", "💫", "🔮", "🌙"],
}
