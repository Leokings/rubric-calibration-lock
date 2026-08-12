# Security and correctness audit

Audit scope: `contracts/RubricCalibrationLock.py` version 0.2.0, the off-chain commitment utility, and direct/integration tests.

## Outcome

The independent review found no critical or high-severity issue. Three medium findings and lower-severity hardening gaps were remediated in version 0.2.0. Static SDK validation, strict type checking, direct state-machine tests, explicit validator tests, and five-validator GLSim integration remain required release gates; exact source-bound evidence belongs in `TEST_RESULTS.md` and `evidence/`.

## Remediated findings

### Medium — post-deadline calibration race

Version 0.1.0 allowed `calibrate()` after `reveal_deadline_unix`, while any caller could simultaneously terminalize the REVEALING state as expired. Version 0.2.0 rejects calibration once the deadline has passed. The exact deadline remains open and the next second is closed, matching commit, reveal, and expiry boundaries.

### Medium — hosted commitment-preview disclosure

Version 0.1.0 exposed a public view that accepted unrevealed example text, expected label, and salt. A hosted RPC operator could observe those arguments even though they were not committed on-chain. Version 0.2.0 removes that public method. `scripts/commitment.py` reproduces the contract digest in a trusted local process, and all tests use it.

### Medium — aggregate calibration prompt could exceed its runtime budget

Individually valid rubric and anchor values could combine into a calibration prompt that exceeded the runtime ceiling only after every commitment and reveal had become immutable. Version 0.2.0 now rejects such a configuration at deployment using a conservative full-anchor prompt calculation with worst-case JSON escaping. Runtime character and UTF-8-byte checks remain in place.

### Low — resource, testing, and evidence hardening

Version 0.2.0 adds UTF-8 byte limits alongside character limits, bounds raw and canonicalized LLM responses, tests unauthorized calibration and deadline boundaries, narrows prompt-injection claims to schema confinement, permits intentionally sanitized deployment proof files, and retains a sanitized historical GLSim transcript.

Remediated finding groups: 4 total (3 Medium, 1 Low). Open findings after remediation: Critical 0, High 0, Medium 0, Low 0.

## Properties reviewed

- Immutable deployment configuration and digest domain separation.
- Commit/reveal binding and non-disclosure before reveal.
- Controller permissions and permissionless objective expiry.
- Deadline boundary consistency (`<=` remains open; `>` rejects reveal and calibration and permits expiry).
- Duplicate anchor ID, commitment, reveal, and terminal-call prevention.
- Exact LLM schema, output count/order, closed labels, and abstention behavior.
- Independent validator rerun and exact canonical result comparison.
- Threshold and denominator math, label-set coverage, and terminal reasons.
- State changes occur only after a validated non-deterministic result.
- Quoted-data and strict-schema boundaries without an immunity claim, Unicode controls, UTF-8 byte limits, collection sizes, prompt limits, and response limits.
- Downstream activation is bound to the exact configuration digest.
- Public policy views serialize the controller as stable lowercase hexadecimal text.
- Native value rejection on deployment and every write method.

## Accepted limitations

### Informational — consensus disagreement affects liveness

If leader and validators classify an anchor differently, GenLayer rejects or rotates the calibration transaction; it cannot truthfully persist that disagreement from inside a result the validators did not accept. State remains `REVEALING`. The controller may retry while the window is open, and anyone may lock `DIVERGENT` after the reveal deadline. This is an explicit consensus boundary, not a hidden `ACTIVE` path.

### Informational — anchor quality is governance, not cryptography

The contract proves correct binding and deterministic comparison against the chosen labels. It cannot prove that anchors are representative, unbiased, independently authored, or free from leakage. Consumers must inspect the revealed set and controller identity.

### Informational — model prompts are ground-truth blind, operators are not

Expected labels are public after reveal. The contract deliberately excludes them from leader and validator LLM prompts, but validator operators can inspect public state. The protocol therefore proves faithful prompt execution under GenLayer's validator assumptions, not cryptographic blindness from operators. A stricter design would require separate text and label commitments and a later scoring phase.

### Informational — activation is composable, not globally enforceable

The contract exposes `is_active(config_digest)` and an auditable terminal record. A downstream application can ignore that view or call a different deployment. Integrators must pin the intended address and digest.

### Informational — public reveal and model drift

All examples, labels, and salts become public after reveal. A passing calibration is historical evidence for that validator execution, not a perpetual guarantee for another model or future production cases.

## Re-audit triggers

Re-audit after any runner change, storage-layout edit, change to commitment framing, looser output comparison, new administrative method, altered threshold math, downstream execution hook, or upgrade mechanism.

## Current verification snapshot

- Open findings: Critical 0, High 0, Medium 0, Low 0.
- Direct suite: 76 passed.
- Current contract SHA-256: `6223c37b31351b7b121effd34323152dbb1ec5c187b7e233eb434026f3f8b28e`.
- Commitment utility SHA-256: `23695b7b2e7c0314860771cb562aea83684ae6cfce5cf65bafbf24113a954239`.
- Current-source five-validator GLSim: passed 2/2 with five explicit mock validators.
- Current-source StudioNet: passed no-mock hosted lifecycle at `0xD0E7AD1037500E9EFF26A711Fa09075E2d545674`; exact source; `ACTIVE`, 3/3 correct and classified, 10,000 bps accuracy and coverage.
- Current-source Bradbury proof: pending.

The retained historical GLSim transcript and `studionet-2026-08-12-proof.json` match contract SHA-256 `801a2394a0f4d55f5df85467a1d6aa58a6322c0a5bb136c29c66093d80f19709`; both are explicitly superseded. The current-source proof is `deployments/studionet-2026-08-12-current-proof.json`. Its harness retained neither receipts nor validator identities, votes, vote count, or model names, so the audit makes no such claims.
