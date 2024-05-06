"""
文字列から絵文字とカスタム絵文字を抽出・リスト化するためのモジュール
TODO:
- 絵文字とカスタム絵文字を順番にリスト化できる関数の実装
"""

import emoji
import re

REGEXP_CUSTOM_EMOJI = r'<a?:[-_.a-zA-Z0-9:[0-9]+>'
REGEXP_ALL_EMOJI = '|'.join([*(re.escape(e) for e in emoji.EMOJI_DATA), r"<a?:[a-z0-9_]+:[0-9]+>"])


def extract_unicode_emojis(text) -> list[str]:
    return [c for c in text if emoji.is_emoji(c)]


def extract_custom_emojis(text) -> list[str]:
    return re.findall(REGEXP_CUSTOM_EMOJI, text)


def extract_emojis(text) -> list[str]:
    return re.findall(REGEXP_ALL_EMOJI, text)


async def convert_emoji(emoji: str | int, guild) -> str:
    if isinstance(emoji, int):
        return str(await guild.fetch_emoji(emoji))
    return emoji
