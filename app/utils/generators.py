import random
import re
import string
import unicodedata


def get_random_string(length):
    return "".join(random.choice(string.ascii_letters) for _ in range(length))


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    text = re.sub(r"^-+|-+$", "", text)
    return text
