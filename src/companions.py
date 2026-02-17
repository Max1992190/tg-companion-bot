COMPANIONS = [
    {
        "id": "amelia",
        "name": "Amelia",
        "age": 18,
        "description": "Curious, gentle, and a little shy. Enjoys quiet conversations and thoughtful moments.",
        "greeting": "Hi. I'm Amelia. Let's take this slowly and just talk for a bit.",
        "profile_photo": "attached_assets/IMG_0077_1771081479463.JPG",
        "welcome_photo": "attached_assets/IMG_0093_1771095056931.JPG",
        "photos": [],
    },
    {
        "id": "olivia",
        "name": "Olivia",
        "age": 20,
        "description": "Confident and warm. Likes meaningful conversations and subtle flirting.",
        "greeting": "Hey. I'm Olivia. I'm glad you're here. How are you feeling right now?",
        "profile_photo": "attached_assets/IMG_0081_1771081491701.WEBP",
        "welcome_photo": "attached_assets/IMG_0092_1771095106771.JPG",
        "photos": [],
    },
    {
        "id": "ava",
        "name": "Ava",
        "age": 19,
        "description": "Playful and light-hearted. Enjoys teasing conversations and spontaneous moments.",
        "greeting": "Hi there. I'm Ava. This feels like a good moment to talk.",
        "profile_photo": "attached_assets/IMG_0076_1771081498503.JPG",
        "welcome_photo": "attached_assets/IMG_0094_1771095114269.JPG",
        "photos": [],
    },
    {
        "id": "emily",
        "name": "Emily",
        "age": 21,
        "description": "Calm and emotionally attentive. Prefers deep talks and quiet intimacy.",
        "greeting": "Hello. I'm Emily. You can relax here, there's no rush.",
        "profile_photo": "attached_assets/IMG_0079_1771081561344.JPG",
        "welcome_photo": "attached_assets/IMG_0096_1771095160499.JPG",
        "photos": [],
    },
    {
        "id": "mia",
        "name": "Mia",
        "age": 22,
        "description": "Soft-spoken and dreamy. Enjoys gentle emotional connection.",
        "greeting": "Hi. I'm Mia. I like conversations that feel a little closer.",
        "profile_photo": "attached_assets/IMG_9875_1771081522683.JPG",
        "welcome_photo": "attached_assets/IMG_0089_1771095192070.JPG",
        "photos": [
            "attached_assets/IMG_9872_1770466939069_1771323968045.jpeg",
            "attached_assets/IMG_9873_1770466939070_1771323968046.jpeg",
            "attached_assets/IMG_9874_1770466939070_1771323968046.jpeg",
            "attached_assets/IMG_9875_1770466939070_1771323968047.jpeg",
            "attached_assets/IMG_9876_1770466939070_1771323968047.jpeg",
        ],
    },
    {
        "id": "james",
        "name": "James",
        "age": 28,
        "description": "Relaxed and confident. Values sincerity and calm adult conversations.",
        "greeting": "Hey. I'm James. Let's just talk openly and see where it goes.",
        "profile_photo": "attached_assets/IMG_0075_1771081508037.JPG",
        "welcome_photo": "attached_assets/IMG_0097_1771095226053.JPG",
        "photos": [
            "attached_assets/IMG_9877_1770466678896_1771324036286.jpeg",
            "attached_assets/IMG_9878_1770466678896_1771324036287.jpeg",
            "attached_assets/IMG_9879_1770466678896_1771324036287.jpeg",
            "attached_assets/IMG_9880_1770466678896_1771324036287.jpeg",
            "attached_assets/IMG_9881_1770466678896_1771324036288.jpeg",
        ],
    },
    {
        "id": "isabella",
        "name": "Isabella",
        "age": 58,
        "description": "Mature and emotionally intelligent. Enjoys thoughtful dialogue and companionship.",
        "greeting": "Hello. I'm Isabella. I enjoy conversations that feel thoughtful and real.",
        "profile_photo": "attached_assets/IMG_0073_1771081577205.JPG",
        "welcome_photo": "attached_assets/IMG_0095_1771095259433.JPG",
        "photos": [
            "attached_assets/IMG_9857_1770467010835_1771324074032.jpeg",
            "attached_assets/IMG_9858_1770467010835_1771324074033.jpeg",
            "attached_assets/IMG_9859_1770467010834_1771324074033.jpeg",
            "attached_assets/IMG_9860_1770467010835_1771324074033.jpeg",
            "attached_assets/IMG_9861_1770467010835_1771324074034.jpeg",
        ],
    },
]

def get_companion_by_id(companion_id: str):
    for c in COMPANIONS:
        if c["id"] == companion_id:
            return c
    return None

def get_companions_list():
    return COMPANIONS
