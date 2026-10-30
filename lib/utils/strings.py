


def shorten(text: str, threshold: int = 50) -> str:
    """
    Shorten a string by replacing its middle with an ellipsis if it exceeds
    the specified character threshold.

    Args:
        text (str): The string to shorten.
        threshold (int, optional): Maximum desired string length. Defaults to 50.

    Returns:
        str: The original string if within the threshold, otherwise a shortened
             version preserving the beginning and end.
    """
    
    if len(text) <= threshold:
        return text

    return f"{text[:threshold // 2 - 2]}...{text[-(threshold // 2 - 1):]}"