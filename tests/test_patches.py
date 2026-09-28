from automata.fa.dfa import DFA

import automata_extensions  # noqa: F401  (applique le patch)
from automata_extensions.utils.patches import patch_cached_method


def test_patch_idempotent():
    assert patch_cached_method() is False  # déjà appliqué à l'import


def test_chained_call_on_temporary_pure_dfa():
    d = DFA(states={"0"}, input_symbols={"a"}, transitions={"0": {"a": "0"}},
            initial_state="0", final_states={"0"})
    for _ in range(50):
        assert (d - d).isempty() is True


def test_clear_cache_still_works(d):
    assert d.isempty() is False
    d.clear_cache()
    assert d.isempty() is False
