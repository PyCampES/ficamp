import pytest

from ficamp.classifier.preprocessing import (
    preprocess,
    remove_digits,
)


@pytest.mark.parametrize(
    ("inp,exp"),
    (
        ("sepa", "sepa"),
        ("123", ""),
        ("sepa12", "sepa12"),  #  it has only 2 digits
        ("sepa123", ""),
        ("sepa 123", "sepa"),
        ("sepa 123", "sepa"),
        ("sepa 12312321 bic", "sepa bic"),
        ("sepa 12312321 123bic", "sepa"),
    ),
)
def test_remove_digits(inp, exp):
    assert remove_digits(inp) == exp


@pytest.mark.parametrize(
    ("inp,exp"),
    (
        ("SEPA", "sepa"),
        ("123", ""),
        ("sepa12", "sepa12"),  #  it has only 2 digits
        ("SEPA123", ""),
        ("SEPA 123", "sepa"),
        ("SEPA 123", "sepa"),
        ("SEPA 12312321 bic", "sepa bic"),
        ("SEPA 12312321 123BIC", "sepa"),
    ),
)
def test_preprocess(inp, exp):
    assert preprocess(inp) == exp
