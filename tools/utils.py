import re


def strip_think(text: str) -> str:
    """Remove <think>...</think> blocks from model output."""
    if not isinstance(text, str):
        return text

    # Remove entire <think>...</think> including multiline
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    return text.strip()
