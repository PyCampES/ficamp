import features


def preprocess(inp: dict):
    """
    Each preprocessing step takes a dict and returns a dict.
    It is assumed that each steps knows how to deal with the content
    of the input received.
    """
    steps = (
        features.make_lowercase,
        features.remove_numbers,
        features.has_iban,
        features.extract_city,
        features.extract_payment_method,
    )
    out = inp
    for func in steps:
        out = func(out)
    return out


preproc = preprocess({"desc": "HELLO world"})
feats = features.get_features(preproc)
encoded = features.one_hot_encode(feats)
