# Verified test results

Recorded on 2026-08-12 against Rubric Calibration Lock version 0.2.0.

| Check | Result |
|---|---|
| `genvm-lint check contracts/RubricCalibrationLock.py --json` | Passed: lint 3/3; SDK validation passed; 10 public methods (5 view, 5 write); 9 constructor parameters |
| `genvm-lint typecheck contracts/RubricCalibrationLock.py --json` | Passed: zero diagnostics |
| `pytest tests/direct -q` | Passed: 76/76 |
| Current-source five-validator GLSim integration | Passed: 2/2 with five explicit mock validators |
| Current-source hosted StudioNet semantic integration | Passed: 1/1; exact source; `ACTIVE`, 3/3 correct/classified, 10,000 bps accuracy/coverage |
| Current-source Bradbury deployment and smoke test | Pending |

Current source hashes:

```text
contracts/RubricCalibrationLock.py
6223c37b31351b7b121effd34323152dbb1ec5c187b7e233eb434026f3f8b28e

scripts/commitment.py
23695b7b2e7c0314860771cb562aea83684ae6cfce5cf65bafbf24113a954239
```

## Current-source StudioNet evidence

The no-mock hosted lifecycle passed at `0xD0E7AD1037500E9EFF26A711Fa09075E2d545674`. Deployed-source readback exactly matched the current 26,165-byte contract at SHA-256 `6223c37b31351b7b121effd34323152dbb1ec5c187b7e233eb434026f3f8b28e`. All nine writes were requested at `FINALIZED` and checked for execution success. Durable state returned `ACTIVE / CALIBRATION_THRESHOLDS_MET`, 3 commitments, 3 reveals, 3 correct predictions, 3 classified predictions, 10,000-basis-point accuracy, and 10,000-basis-point coverage. The harness retained no receipts or transaction hashes and exposed no validator identities, votes, vote count, or model names. See [`deployments/studionet-2026-08-12-current-proof.json`](deployments/studionet-2026-08-12-current-proof.json).

## Superseded source-bound evidence

The retained historical GLSim transcript and hosted `studionet-2026-08-12-proof.json` match the earlier contract SHA-256 `801a2394a0f4d55f5df85467a1d6aa58a6322c0a5bb136c29c66093d80f19709`, not the current source. They remain useful historical evidence but are ineligible for a current-source submission.

The historical GLSim cases verified a complete off-chain-commitment/reveal/calibration flow with five separate mocked validator profiles and a malformed consensus output that failed without a terminal state transition. Its sanitized command, hashes, cases, timing, and interpretation remain in [`evidence/glsim-2026-08-12.txt`](evidence/glsim-2026-08-12.txt).

The historical StudioNet smoke requested all nine write receipts at `FINALIZED`, observed successful execution, and read back `ACTIVE` with config digest `1c2ebb918cb22d9e39a89d0d455d61fedee7bb2c82de18ab14779f50675b9c12` and terminal digest `051c4d5f954257d1aa9c7bd87e30d7982b5e3859bd3edd837db3e85a2809bed7`. See [`deployments/studionet-2026-08-12-proof.json`](deployments/studionet-2026-08-12-proof.json). The runner did not retain transaction hashes or expose validator votes/models, and the standalone CLI could not retrieve the address after the test process exited. It is session-scoped, superseded evidence—not a current-source Explorer deployment or heterogeneous-model claim.
