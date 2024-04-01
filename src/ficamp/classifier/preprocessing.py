import string


def remove_digits(s: str) -> str:
    """
    Return string without words that have more that 2 digits.
    examples:
        like SEPA 12312321 BIC --> SEPA BIC
        like SEPA12 --> SEPA12
    """
    clean = []
    words = s.split()

    for word in words:
        n_char = 0
        for char in word:
            n_char += char.isdigit()
        if n_char <= 2:
            clean.append(word)
    return " ".join(clean)


def remove_pipes(s: str) -> str:
    return " ".join(s.split("|"))


def remove_colon(s: str) -> str:
    return " ".join(s.split(":"))


def remove_comma(s: str) -> str:
    return " ".join(s.split(","))


def remove_punctuation(s: str) -> str:
    punctuation = set(string.punctuation)
    out = "".join((" " if char in punctuation else char for char in s))
    return " ".join(out.split())  # Remove double spaces


def remove_isolated_digits(s: str) -> str:
    """Remove words made only of digits"""
    digits = set(string.digits)
    clean = []
    for word in s.split():
        if not all((char in digits for char in word)):
            clean.append(word)
    return " ".join(clean)


def preprocess(s: str) -> str:
    "Clean up transaction description"
    steps = (
        lambda s: s.lower(),
        remove_pipes,
        remove_colon,
        remove_comma,
        remove_digits,
        remove_punctuation,
        remove_isolated_digits,
    )
    out = s
    for func in steps:
        out = func(out)
    return out
