def test_reverse_dfa_accepts_mirror(d):
    rev = d.reverse()
    assert rev.accepts_input("aaa") == d.accepts_input("aaa")  # palindrome de test
    assert rev.determinize().accepts_input("aa") == d.accepts_input("aa")


def test_reverse_reverse_equivalent_to_self(d):
    twice = d.reverse().determinize().reverse().determinize()
    assert twice.is_equivalent(d)


def test_reverse_specific_word():
    from automata_extensions.fa import ExtendedDFA
    dfa = ExtendedDFA(
        states={"q0", "q1"}, input_symbols={"a", "b"},
        transitions={"q0": {"a": "q1", "b": "q0"}, "q1": {"a": "q1", "b": "q1"}},
        initial_state="q0", final_states={"q1"},
    )
    # L = mots contenant 'a' ; miroir(L) = mots contenant 'a' aussi (symétrique)
    rev = dfa.reverse().determinize()
    assert rev.accepts_input("ba")
    assert not rev.accepts_input("bb")
