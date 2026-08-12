# Rubric Calibration Lock

A standalone, MIT-licensed GenLayer Intelligent Contract that prevents an immutable, bounded rubric from becoming usable until decentralized validators can classify committed and revealed anchor examples consistently enough to meet configured overall-accuracy and coverage thresholds.

This is a calibration gate, not a deliverable evaluator. It never scores production submissions, interprets executable policy, releases funds, or updates the rubric. Other contracts may read `is_active(config_digest)` and the terminal calibration record before trusting a separately implemented evaluator that is pinned to the same rubric digest.

## Why GenLayer

Whether a natural-language example belongs to one closed label is a semantic judgment. The leader classifies every revealed anchor and validators independently perform the same bounded classification. Their consensus-critical output is only the exact ordered label vector. Deterministic contract code compares it with the committed ground-truth labels, computes basis-point accuracy and coverage, and irreversibly locks `ACTIVE` or `DIVERGENT`.

## Lifecycle

1. Deploy an immutable rubric, 2-8 closed labels, anchor count, thresholds, and deadlines.
2. The controller locally computes and submits 3-16 domain-separated hashes. Text, expected labels, and salts are not stored on-chain before reveal; confidentiality additionally requires private off-chain handling and random salts.
3. Once every commitment is present, the controller opens the reveal phase early.
4. The controller reveals each text, expected label, and random 32-byte hexadecimal salt. Exact commitment binding is checked on-chain.
5. Before the reveal/calibration deadline, `calibrate()` asks the leader and validators to independently return one exact label—or `UNCLASSIFIED`—for every anchor.
6. Deterministic code locks the rubric `ACTIVE` only if the expected anchor set covers every configured label and both thresholds pass. Every other completed calibration becomes `DIVERGENT`.
7. Missing commitments, missing reveals, or failure to calibrate can be permissionlessly terminalized after the applicable deadline.

Deployment also rejects any configuration whose conservative full-calibration prompt could exceed the UTF-8 budget after worst-case JSON escaping across all anchors. Runtime checks independently cap prompt size and both raw and canonicalized LLM responses.

## Stable interface

```python
commit_anchor(anchor_id, commitment)
open_reveal()
reveal_anchor(anchor_id, example_text, expected_label, salt)
calibrate()
lock_expired()

get_policy() -> dict
get_calibration() -> dict
get_anchor(anchor_id) -> dict
get_anchor_id(index) -> str
is_active(expected_config_digest) -> bool
```

Commitments must be computed in a trusted local process with [`scripts/commitment.py`](scripts/commitment.py). The contract intentionally exposes no public preview endpoint because a hosted RPC operator would receive its private arguments. Read the public configuration digest and label set, then call:

```python
from scripts.commitment import compute_anchor_commitment

commitment = compute_anchor_commitment(
    config_digest,
    anchor_id,
    example_text,
    expected_label,
    random_salt_hex,
    allowed_labels,
)
```

The helper also accepts one JSON object on standard input and prints only the digest. Generate salts with a cryptographically secure local generator such as `secrets.token_hex(32)` and never reuse them.

`is_active` binds consumers to the exact deployment and immutable configuration digest. A consumer should additionally decide whether it trusts the controller, anchor design, thresholds, and deployment address.

## Quick verification

```powershell
genvm-lint check contracts/RubricCalibrationLock.py
genvm-lint typecheck contracts/RubricCalibrationLock.py
pytest tests/direct -v
```

For five-validator GLSim instructions and hosted-network notes, see [TESTING.md](TESTING.md). Design and threat boundaries are in [ARCHITECTURE.md](ARCHITECTURE.md) and [SECURITY.md](SECURITY.md).

The current source has 76 passing direct tests and passed both five-validator GLSim tests with explicit mocks. A no-mock StudioNet lifecycle deployed the exact 26,165-byte current source at `0xD0E7AD1037500E9EFF26A711Fa09075E2d545674`, finalized all nine writes successfully, and locked `ACTIVE` after 3/3 correct and classified anchors at 10,000-basis-point accuracy and coverage. The harness did not retain receipts or expose validator votes, identities, or model names, so none are claimed. Bradbury remains pending. See [TEST_RESULTS.md](TEST_RESULTS.md) and [`deployments/studionet-2026-08-12-current-proof.json`](deployments/studionet-2026-08-12-current-proof.json).

## Scope boundary

The contract establishes only that one immutable rubric crossed a declared calibration threshold on one disclosed anchor set. `accuracy_bps` uses all anchors as its denominator, so an `UNCLASSIFIED` prediction counts as incorrect and also lowers coverage. Expected labels become public when revealed; they are omitted from the LLM prompt, but the protocol does not claim operator-blind evaluation. It is not proof of general model accuracy, evaluator permanence, legal compliance, fairness, or performance on later real-world inputs. Anchor quality and representativeness remain the deployer's responsibility.

## License

MIT. See [LICENSE](LICENSE).
