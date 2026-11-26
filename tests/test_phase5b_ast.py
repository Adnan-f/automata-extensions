import pytest

from automata_extensions.regex import (EMPTY, EPSILON, RegexSyntaxError, Symbol,
                                       concat, parse, star, union)


def test_parse_str_roundtrip_simple():
    for text in ["a", "ab", "a|b", "a*", "(a|b)*abb", "a?b", "a\\*b"]:
        assert str(parse(text).simplify()) == text


def test_parse_epsilon_forms():
    assert parse("") == EPSILON
    assert parse("()") == EPSILON
    assert str(EPSILON) == "()"


def test_parse_plus_and_optional_are_desugared():
    assert str(parse("a+").simplify()) == "aa*"
    assert str(parse("a?").simplify()) == "a?"


@pytest.mark.parametrize("bad", ["(a", "a)", "*a", "a||b", "|a", "a|", "\\"])
def test_parse_syntax_errors(bad):
    with pytest.raises(RegexSyntaxError):
        parse(bad)


def test_simplify_rules():
    assert parse("a|a").simplify() == Symbol("a")
    assert str(parse("b|a").simplify()) == "a|b"           # tri canonique
    assert str(parse("a**").simplify()) == "a*"
    assert str(parse("(a|())*").simplify()) == "a*"        # (ε|r)* = r*
    assert str(parse("()a()").simplify()) == "a"           # ε neutre
    assert parse("a*").simplify().nullable()


def test_smart_constructors_empty_and_epsilon():
    a = Symbol("a")
    assert union(EMPTY, a) == a
    assert concat(EMPTY, a) == EMPTY
    assert concat(EPSILON, a) == a
    assert star(EMPTY) == EPSILON
    assert union() == EMPTY and concat() == EPSILON
    assert str(EMPTY) == "∅"


def test_nullable():
    assert parse("a*").nullable()
    assert parse("a?").nullable()
    assert not parse("a+").nullable()
    assert parse("(a|b)*").nullable()
    assert not parse("ab").nullable()


def test_symbols_and_size():
    r = parse("(a|b)*c")
    assert r.symbols() == {"a", "b", "c"}
    assert r.size() > 3


def test_derivatives():
    r = parse("(a|b)*abb").simplify()
    da = r.derivative("a")
    # a^{-1}((a|b)*abb) = (a|b)*abb | bb
    assert da.nullable() is False
    assert da.derivative("b").derivative("b").nullable() is True
    assert r.derivative("c") == EMPTY or not r.derivative("c").nullable()


def test_escaped_special_symbols():
    r = parse("\\(a\\)")
    assert r.symbols() == {"(", "a", ")"}
    assert str(r.simplify()) == "\\(a\\)"
