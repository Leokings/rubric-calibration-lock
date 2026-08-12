import pytest

from scripts.commitment import CommitmentInputError, compute_anchor_commitment


CONFIG_DIGEST = "1" * 64
ANCHOR_ID = "ANCHOR-01"
EXAMPLE = "Saving an existing document crashes the application every time."
LABELS = ["BUG", "FEATURE"]
SALT = "a" * 64


def compute(**overrides):
    values = {
        "config_digest": CONFIG_DIGEST,
        "anchor_id": ANCHOR_ID,
        "example_text": EXAMPLE,
        "expected_label": "BUG",
        "salt": SALT,
        "allowed_labels": LABELS,
    }
    values.update(overrides)
    return compute_anchor_commitment(**values)


def test_known_commitment_vector_is_stable():
    assert compute() == "a54eba36369a3077cdbcac9be00d945ad86688665fa5e4ff3b7e9206a158dcfa"


def test_offchain_utility_uses_contract_whitespace_canonicalization():
    assert compute(example_text="  Saving   an existing document crashes the application every time.  ") == compute()


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"salt": "A" * 64}, "SALT"),
        ({"expected_label": "UNKNOWN"}, "EXPECTED_LABEL_UNKNOWN"),
        ({"anchor_id": "bad id"}, "ANCHOR_ID"),
        ({"example_text": "\u00e9" * 601}, "EXAMPLE_TEXT"),
        ({"example_text": "\ud800" * 12}, "EXAMPLE_TEXT"),
    ],
)
def test_offchain_utility_rejects_preimages_the_contract_would_reject(overrides, message):
    with pytest.raises(CommitmentInputError, match=message):
        compute(**overrides)
