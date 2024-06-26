import pytest

from ficamp.classifier.preprocessing import (
    preprocess,
    remove_colon,
    remove_comma,
    remove_digits,
    remove_isolated_digits,
    remove_pipes,
    remove_punctuation,
    remove_short_words,
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
        ("CSIDNL0213324324324", "CSIDNL0213324324324"),
        ("CSID:NL0213324324324", "CSID NL0213324324324"),
    ),
)
def test_remove_colon(inp, exp):
    assert remove_colon(inp) == exp


@pytest.mark.parametrize(
    ("inp,exp"),
    (("CSID,NL0213324324324", "CSID NL0213324324324"),),
)
def test_remove_comma(inp, exp):
    assert remove_comma(inp) == exp


@pytest.mark.parametrize(
    ("inp,exp"),
    (
        ("hello world", "hello world"),
        ("hello/world", "hello world"),
        ("hello.world", "hello world"),
        ("hello.(.world))", "hello world"),
    ),
)
def test_remove_punctuation(inp, exp):
    assert remove_punctuation(inp) == exp


@pytest.mark.parametrize(
    ("inp,exp"),
    (
        ("hello22 world", "hello22 world"),
        ("hello 22 world", "hello world"),
    ),
)
def test_remove_isolated_digits(inp, exp):
    assert remove_isolated_digits(inp) == exp


@pytest.mark.parametrize(
    ("inp,exp"),
    (
        ("hello a world", "hello world"),
        ("hello aa world", "hello aa world"),
    ),
)
def test_remove_short_words(inp, exp):
    assert remove_short_words(inp) == exp


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
        ("CSID:NL0213324324324", "csid"),
        ("CSID:NL0213324324324 HELLO,world1332", "csid hello"),
        ("CSID:NL021332432 N26 HELLO,world1332", "csid n26 hello"),
        ("CSID:NL021332432 4324 HELLO,world1332", "csid hello"),
        ("CSID:NL021332432 n. HELLO,world1332", "csid hello"),
    ),
)
def test_preprocess(inp, exp):
    assert preprocess(inp) == exp
