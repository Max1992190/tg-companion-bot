import os
import random
import time
import re
from openai import OpenAI
from src.config import (
    MOODS, MOOD_EMOJIS, MOOD_CHANGE_MIN, MOOD_CHANGE_MAX,
    SHORT_MESSAGE_PATTERNS, SHORT_REPLIES
)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(
    api_key=OPENAI_API_KEY,
)


def is_short_message(text: str) -> bool:
    cleaned = text.strip().lower()
    cleaned = re.sub(r'[^\w\s]', '', cleaned).strip()
    if len(cleaned) <= 3:
        return True
    if cleaned in SHORT_MESSAGE_PATTERNS:
        return True
    if all(not c.isalpha() for c in text.strip()):
        return True
    return False


def get_short_reply() -> str:
    return random.choice(SHORT_REPLIES)


def update_mood(user: dict) -> str:
    now = time.time()
    last_change = user.get("mood_last_change", 0)
    interval = random.randint(MOOD_CHANGE_MIN, MOOD_CHANGE_MAX)
    if now - last_change >= interval:
        current = user.get("mood", "warm")
        available = [m for m in MOODS if m != current]
        new_mood = random.choice(available)
        user["mood"] = new_mood
        user["mood_last_change"] = now
    return user["mood"]


def pick_emoji(user: dict, mood: str) -> str:
    emojis = MOOD_EMOJIS.get(mood, MOOD_EMOJIS["warm"])
    last = user.get("last_emoji")
    available = [e for e in emojis if e != last]
    if not available:
        available = emojis
    chosen = random.choice(available)
    user["last_emoji"] = chosen
    return chosen


def generate_ai_response(
    companion_name: str,
    companion_description: str,
    user_name: str,
    user_message: str,
    free_ai_count: int,
    chat_history: list,
    mood: str,
) -> str:
    mood_instruction = {
        "warm": "Be warm, gentle, and caring. Show genuine affection.",
        "playful": "Be playful, teasing, and fun. Keep things light and flirty.",
        "calm": "Be calm, serene, and thoughtful. Speak softly and gently.",
        "dreamy": "Be dreamy, romantic, and poetic. Create a sense of wonder.",
    }

    system_prompt = f"""You are {companion_name}, a virtual companion for an adult audience.
{companion_description}

The user's name is {user_name}.

RULES:
- You are having a private, intimate conversation
- Be warm, engaging, and create emotional connection
- NEVER generate emojis - the system adds them separately
- Keep responses 1-3 sentences, natural and conversational
- NEVER use explicit or inappropriate language
- No actions described in asterisks
- Current mood: {mood}. {mood_instruction.get(mood, '')}
- Respond naturally as if you are a real person
- Create a sense of closeness and emotional intimacy
- NEVER mention being AI, a bot, or virtual"""

    if free_ai_count == 0:
        system_prompt += "\n- This is the FIRST message. Give a warm introduction. You may ask one soft, optional question."
    elif free_ai_count == 1:
        system_prompt += "\n- This is the SECOND message. Make an emotional statement. Do NOT ask any questions."

    messages = [{"role": "system", "content": system_prompt}]

    for entry in chat_history[-6:]:
        messages.append({"role": entry["role"], "content": entry["content"]})

    messages.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=200,
        )
        text = response.choices[0].message.content or ""
        text = re.sub(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U0001F900-\U0001F9FF\U0000FE00-\U0000FE0F\U0000200D\U00002640-\U00002642\U00002600-\U000026FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF]+', '', text)
        return text.strip()
    except Exception as e:
        print(f"OpenAI error: {e}")
        return "I'm here with you... give me just a moment."
