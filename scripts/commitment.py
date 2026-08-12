"""Compute Rubric Calibration Lock anchor commitments entirely off-chain.

The hosted contract deliberately does not expose a commitment-preview method:
sending an unrevealed example, expected label, and salt to a public RPC endpoint
would disclose the preimage to that operator. Import ``compute_anchor_commitment``
in a trusted local process, or pipe one JSON object to this module's CLI.
"""

from __future__ import annotations

import json
import sys
from collections.abc import Sequence

from eth_hash.auto import keccak


DIGEST_DOMAIN = "GENLAYER_RUBRIC_CALIBRATION_LOCK"
ABSTAIN_LABEL = "UNCLASSIFIED"
MAX_ANCHOR_ID_CHARS = 64
MIN_EXAMPLE_CHARS = 12
MAX_EXAMPLE_CHARS = 1200


class CommitmentInputError(ValueError):
    """Raised when a preimage would be rejected by the on-chain contract."""


def _canonical_text(value: str, label: str, minimum: int, maximum: int) -> str:
    if (
        not isinstance(value, str)
        or len(value) > maximum * 2
    ):
        raise CommitmentInputError(label)
    for character in value:
        codepoint = ord(character)
        if (
            codepoint <= 31
            or 127 <= codepoint <= 159
            or 55296 <= codepoint <= 57343
            or codepoint in (173, 1564, 6158, 8203, 8204, 8205, 8206, 8207, 8288, 65279)
            or 8232 <= codepoint <= 8238
            or 8294 <= codepoint <= 8303
            or 65529 <= codepoint <= 65531
            or 917504 <= codepoint <= 917631
        ):
            raise CommitmentInputError(label)
    if len(value.encode("utf-8")) > maximum * 2:
        raise CommitmentInputError(label)
    normalized = " ".join(value.split())
    if (
        len(normalized) < minimum
        or len(normalized) > maximum
        or len(normalized.encode("utf-8")) > maximum
    ):
        raise CommitmentInputError(label)
    return normalized


def _canonical_identifier(value: str, label: str, maximum: int) -> str:
    normalized = _canonical_text(value, label, 1, maximum)
    for character in normalized:
        if not (
            "A" <= character <= "Z"
            or "0" <= character <= "9"
            or character in ("_", "-", ".", ":")
        ):
            raise CommitmentInputError(label)
    return normalized


def _canonical_label(value: str) -> str:
    result = _canonical_identifier(value, "EXPECTED_LABEL", 32)
    if result == ABSTAIN_LABEL:
        raise CommitmentInputError("EXPECTED_LABEL_RESERVED")
    return result


def _canonical_digest(value: str, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or value.lower() != value:
        raise CommitmentInputError(label)
    if any(character not in "0123456789abcdef" for character in value):
        raise CommitmentInputError(label)
    return value


def _digest(tag: str, parts: Sequence[str]) -> str:
    framed = ""
    for part in [DIGEST_DOMAIN, tag, *parts]:
        framed += str(len(part)) + ":" + part
    return keccak(framed.encode("utf-8")).hex()


def compute_anchor_commitment(
    config_digest: str,
    anchor_id: str,
    example_text: str,
    expected_label: str,
    salt: str,
    allowed_labels: Sequence[str],
) -> str:
    """Return the exact V2 on-chain anchor commitment.

    ``salt`` must be a cryptographically random, single-use 32-byte lowercase
    hexadecimal value. This function validates its shape, not its entropy.
    """

    canonical_config = _canonical_digest(config_digest, "CONFIG_DIGEST")
    canonical_anchor = _canonical_identifier(anchor_id, "ANCHOR_ID", MAX_ANCHOR_ID_CHARS)
    canonical_example = _canonical_text(
        example_text,
        "EXAMPLE_TEXT",
        MIN_EXAMPLE_CHARS,
        MAX_EXAMPLE_CHARS,
    )
    canonical_label = _canonical_label(expected_label)
    canonical_allowed = [_canonical_label(label) for label in allowed_labels]
    if len(canonical_allowed) < 2 or len(canonical_allowed) > 8:
        raise CommitmentInputError("ALLOWED_LABELS")
    if len(set(canonical_allowed)) != len(canonical_allowed):
        raise CommitmentInputError("ALLOWED_LABELS_DUPLICATE")
    if canonical_label not in canonical_allowed:
        raise CommitmentInputError("EXPECTED_LABEL_UNKNOWN")
    canonical_salt = _canonical_digest(salt, "SALT")
    return _digest(
        "ANCHOR_COMMITMENT",
        [
            canonical_config,
            canonical_anchor,
            canonical_example,
            canonical_label,
            canonical_salt,
        ],
    )


def _reject_duplicate_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise CommitmentInputError("JSON_DUPLICATE_KEY")
        result[key] = value
    return result


def main() -> int:
    """Read a private preimage JSON object from stdin and print only its digest."""

    try:
        payload = json.load(sys.stdin, object_pairs_hook=_reject_duplicate_pairs)
        if not isinstance(payload, dict) or set(payload) != {
            "config_digest",
            "anchor_id",
            "example_text",
            "expected_label",
            "salt",
            "allowed_labels",
        }:
            raise CommitmentInputError("INPUT_FIELDS")
        result = compute_anchor_commitment(
            payload["config_digest"],
            payload["anchor_id"],
            payload["example_text"],
            payload["expected_label"],
            payload["salt"],
            payload["allowed_labels"],
        )
    except (CommitmentInputError, TypeError, ValueError, json.JSONDecodeError) as error:
        print(f"commitment input rejected: {error}", file=sys.stderr)
        return 2
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
