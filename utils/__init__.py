import emoji


def extract_emojis(text) -> list[str]:
    return [c for c in text if emoji.is_emoji(c)]
