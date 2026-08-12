# Security and correctness audit

Audit scope: `contracts/RubricCalibrationLock.py` version 0.2.1, the off-chain commitment utility, and direct/integration tests.

## Outcome

No Critical, High, Medium, or Low finding remains open in v0.2.1. Three Medium findings and lower-severity hardening gaps were remediated in v0.2.0. A subsequent Bradbury semantic smoke exposed one High functional defect in v0.2.0: nondeterministic callbacks indirectly read contract storage, which Bradbury's GenVM rejects. v0.2.1 remediates that defect and adds a regression test. Static SDK validation, strict type checking, direct state-machine tests, explicit validator tests, and five-validator GLSim integration remain required release gates; exact source-bound evidence belongs in `TEST_RESULTS.md` and `evidence/`.

## Remediated findings

### High — nondeterministic callback read contract storage on Bradbury

The byte-exact v0.2.0 deployment finalized, but its principal `calibrate()` path failed before inference on Bradbury. The leader and validator callbacks indirectly accessed `self` storage while running under `gl.vm.run_nondet_unsafe`; GenVM reported that contract-storage reads in nondeterministic mode are unsupported, all five validators recorded deterministic violations, and no terminal state was written. v0.2.1 constructs the complete immutable classification prompt and copies the ordered anchor IDs and labels while execution is deterministic. The callbacks close only over plain local values and perform no contract-storage reads. A direct AST regression test verifies that neither callback contains a `self` reference. The old deployment proof is retained as superseded negative evidence, not as a successful semantic smoke.

### Medium — post-deadline calibration race

Version 0.1.0 allowed `calibrate()` after `reveal_deadline_unix`, while any caller could simultaneously terminalize the REVEALING state as expired. Version 0.2.0 rejects calibration once the deadline has passed. The exact deadline remains open and the next second is closed, matching commit, reveal, and expiry boundaries.

### Medium — hosted commitment-preview disclosure

Version 0.1.0 exposed a public view that accepted unrevealed example text, expected label, and salt. A hosted RPC operator could observe those arguments even though they were not committed on-chain. Version 0.2.0 removes that public method. `scripts/commitment.py` reproduces the contract digest in a trusted local process, and all tests use it.

### Medium — aggregate calibration prompt could exceed its runtime budget

Individually valid rubric and anchor values could combine into a calibration prompt that exceeded the runtime ceiling only after every commitment and reveal had become immutable. Version 0.2.0 now rejects such a configuration at deployment using a conservative full-anchor prompt calculation with worst-case JSON escaping. Runtime character and UTF-8-byte checks remain in place.

### Low — resource, testing, and evidence hardening

Version 0.2.0 adds UTF-8 byte limits alongside character limits, bounds raw and canonicalized LLM responses, tests unauthorized calibration and deadline boundaries, narrows prompt-injection claims to schema confinement, permits intentionally sanitized deployment proof files, and retains a sanitized historical GLSim transcript.

Remediated finding groups: 5 total (1 High, 3 Medium, 1 Low). Open findings after remediation: Critical 0, High 0, Medium 0, Low 0.

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
- Direct suite: 77 passed.
- Current contract SHA-256: `3c403a31fd155dad704394b34c8c3ef6f2d459c3d19babeaec6d13b6262ec66a` (26,546 bytes).
- Commitment utility SHA-256: `23695b7b2e7c0314860771cb562aea83684ae6cfce5cf65bafbf24113a954239`.
- Current-source five-validator GLSim: passed 2/2 with five explicit mock validators.
- Current-source StudioNet: passed no-mock hosted lifecycle at `0xC914Af58d5576dF91898B1AF9ef231B8e65364ca`; exact source; `ACTIVE`, 3/3 correct and classified, 10,000 bps accuracy and coverage.
- Current-source v0.2.1 Bradbury: byte-exact deployment and all eight lifecycle writes finalized successfully with 5/5 agreement; durable `ACTIVE`, 3/3 correct/classified, 10,000 bps accuracy/coverage.

The current-source StudioNet proof is `deployments/studionet-2026-08-12-v0.2.1-current-proof.json`. Its harness retained neither receipts nor validator identities, votes, vote count, or model names, so the audit makes no such claims. The v0.2.0 StudioNet proof at `deployments/studionet-2026-08-12-current-proof.json`, the older source-bound StudioNet/GLSim evidence, and the failed v0.2.0 Bradbury semantic smoke are all explicitly superseded. The Bradbury record remains valuable negative regression evidence for the remediated High finding but is ineligible for Portal submission.
