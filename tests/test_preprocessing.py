import pytest

from ficamp.classifier.preprocessing import (
    preprocess,
    remove_digits,
    remove_pipes,
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
        ("SEPA 1231AMSTERDAM", "SEPA 1231AMSTERDAM"),  # nothing to do
        ("SEPA 1231|AMSTERDAM", "SEPA 1231 AMSTERDAM"),
    ),
)
def test_remove_pipes(inp, exp):
    assert remove_pipes(inp) == exp


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
        ("SEPA 1231|AMSTERDAM 123BIC", "sepa amsterdam"),
    ),
)
def test_preprocess(inp, exp):
    assert preprocess(inp) == exp
