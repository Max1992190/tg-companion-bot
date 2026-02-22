import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set in environment")
OWNER_ID = int(os.environ.get("OWNER_ID" , "0"))

ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))
ADMIN_IDS = [i for i in [OWNER_ID, ADMIN_ID, 8454575259] if i]

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

PHOTO_TRIGGER_WORDS = ["photo", "foto", "pic", "picture", "show me", "send a photo", "send pic", "send photo", "send me a photo", "send me pic"]

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

PHOTO_CAPTIONS = [
    "I thought you might like this… ✨",
    "This one feels a bit special.",
    "Just for you.",
    "I was in the mood to share this.",
    "A little glimpse, just between us.",
    "Tell me what you feel when you see this.",
    "I hesitated… but decided to show you.",
    "This feels right to share right now.",
    "I saved this one for you… 💫",
    "Something about this moment felt right.",
    "I hope this makes you smile.",
    "A little closer, just for tonight…",
    "I wanted you to see this side of me.",
    "Don't look away… 😏",
    "This is just between us, okay?",
]

MOODS = ["warm", "playful", "calm", "dreamy"]

MOOD_EMOJIS = {
    "warm": ["💕", "🥰", "☺️", "💗", "🤗", "💓", "😊"],
    "playful": ["😏", "😜", "🤭", "💋", "😉", "✨", "🫦"],
    "calm": ["🌙", "💫", "🦋", "🌸", "✨", "🌺", "💭"],
    "dreamy": ["🌌", "💭", "🫧", "🌠", "💫", "🔮", "🌙"],
}
