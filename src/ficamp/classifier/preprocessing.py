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


def preprocess(s: str) -> str:
    "Clean up transaction description"
    steps = (
        lambda s: s.lower(),
        remove_pipes,
        remove_digits,
    )
    out = s
    for func in steps:
        out = func(out)
    return out
