from dataclasses import dataclass
from functools import lru_cache
from typing import Any

import numpy as np
from sklearn.utils import murmurhash3_32


@dataclass
class HashFeature:
    cardinality: int


def sort_dict(d):
    return dict(sorted(d.items(), key=lambda x: x[0]))


@lru_cache(500)
def categorical_hash_bucket(item: str, *, buckets: int) -> int:
    """Integer representation of item achieved like this: hash(item) % buckets"""
    if not isinstance(item, str):
        raise ValueError("item must be a string")
    return murmurhash3_32(item, positive=True) % buckets


# def make_lowercase(d):
#     return {"desc": d["desc"].lower()}


def has_iban(d) -> str:
    """
    Return str(int(True)) if IBAN detected, else str(int(False)).
    str because we need string to encode feature"""
    # TODO: remove hardcoded value
    return d | {"has_iban": str(int(True))}


def extract_city(d) -> str:
    "Return city name in lowercase if found, else <UNK>"
    # TODO: remove hardcoded value
    return d | {"city": "Lleida"}


def extract_payment_method(d: dict) -> str | dict[str, Any]:
    "Return payment method name in lowercase if found, else <UNK>"
    # TODO:improve logic

    payment_methods = sorted(
        (
            "card",
            "creditcard",
            "paypal",
            "transfer",
        )
    )
    res = "<UNK>"
    for method in payment_methods:
        if method in d["desc"]:
            return method
    return d | {"payment_method": res}


# This config determines which features will be extracted
# from the transaction description ("desc")
CONFIG = {
    "city": HashFeature(cardinality=100),
    "has_iban": HashFeature(cardinality=2),
    "payment_method": HashFeature(cardinality=10),
}


def get_features(preprocessed: dict):
    features = {}
    for name, conf in CONFIG.items():
        features[name] = categorical_hash_bucket(
            preprocessed[name], buckets=conf.cardinality
        )
    return features


def one_hot_encode(features: dict):
    encoded = {}
    for name, idx in sort_dict(features).items():
        c = CONFIG[name].cardinality
        one_hot = np.zeros(c)
        one_hot[idx] = 1
        encoded[name] = one_hot
    return encoded
