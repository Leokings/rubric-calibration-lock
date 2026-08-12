# Testing

## Static and direct checks

```powershell
python -m pip install -r requirements.txt
genvm-lint check contracts/RubricCalibrationLock.py
genvm-lint typecheck contracts/RubricCalibrationLock.py
pytest tests/direct -v
```

Direct tests cover constructor and UTF-8 byte bounds, conservative aggregate prompt budgeting under worst-case JSON escaping, off-chain commitment vectors and binding, permissions, phase transitions, exact and post-deadline behavior, replay protections, strict schemas, raw/canonical LLM response limits, threshold math, adversarial quoted content, terminal immutability, downstream views, and direct validator acceptance/rejection. The quoted-content cases verify output confinement with mocked inference; they do not establish live-model prompt-injection immunity. Direct mode executes the leader path; explicit `run_validator()` cases exercise the custom validator closure.

Current-source direct result: **76 passed**.

Commitment preimages must never be sent to a hosted contract view. Import `compute_anchor_commitment` from `scripts.commitment`, or pipe a JSON object to `python scripts/commitment.py` in a trusted local environment. The integration suites use that local helper.

## Five-validator GLSim

Terminal 1:

```powershell
python tests/run_glsim.py --port 4112 --validators 5 --no-browser
```

Terminal 2:

```powershell
gltest tests/integration/test_rubric_calibration_lock_glsim.py -v -s --network localnet
```

The frozen current source passed both integration tests with five separate mocked validator profiles and exact bounded responses. This verified consensus/state persistence and fail-closed malformed output. Identical mocks are neither validator-model independence evidence nor a heterogeneous-model quality evaluation. The older historical transcript remains at [`evidence/glsim-2026-08-12.txt`](evidence/glsim-2026-08-12.txt) and is not current-source provenance.

## StudioNet

StudioNet is gasless. Run deployment and the same commit/reveal lifecycle with future deadlines, computing commitments locally, then call `calibrate()` using deliberately clear anchors. Hosted-network semantic results are provider-dependent and should be recorded with contract address, transaction IDs when retained, source hash, configuration digest, terminal digest, and exact observed metrics.

Run the explicit live smoke test with:

```powershell
gltest tests/integration/test_rubric_calibration_lock_live.py -v -s --network studionet
```

Current-source result: **1 passed** in 389.67 seconds. Contract `0xD0E7AD1037500E9EFF26A711Fa09075E2d545674` matched the repository's 26,165-byte source exactly at SHA-256 `6223c37b31351b7b121effd34323152dbb1ec5c187b7e233eb434026f3f8b28e`. The test requested `FINALIZED` for deployment, three commitments, reveal opening, three reveals, and calibration, and asserted execution success for all nine writes. Durable views returned `ACTIVE / CALIBRATION_THRESHOLDS_MET`, 3 commits, 3 reveals, 3 correct, 3 classified, and 10,000-basis-point accuracy and coverage. See [`deployments/studionet-2026-08-12-current-proof.json`](deployments/studionet-2026-08-12-current-proof.json).

The harness did not retain receipts or transaction hashes and did not expose validator identities, votes, vote count, or model names. None are claimed. The earlier [`deployments/studionet-2026-08-12-proof.json`](deployments/studionet-2026-08-12-proof.json) remains explicitly superseded because it matches an older source hash.

## Bradbury

Bradbury requires a funded testnet-only wallet configured through an ignored `.env`. Do not reuse a wallet containing mainnet assets. Deployment records belong in `deployments/`; the included template lists the minimum evidence fields. Sanitized public evidence should be named `*-proof.json` or `*-public.json`, which are intentionally trackable; all other deployment JSON remains ignored.

Current-source Bradbury deployment and smoke-test evidence: **pending**.
