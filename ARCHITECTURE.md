# Architecture

## Consensus boundary

The frontend or integrating application owns anchor authoring, cryptographically secure salt generation, private off-chain commitment computation, transaction submission, indexing, and any later production evaluator. The contract owns immutable configuration, commitment binding, lifecycle enforcement, validator classification consensus, deterministic calibration math, terminal state, and queryable digests.

The only non-deterministic operation is a bounded mapping:

```text
(immutable rubric, closed labels, revealed anchor text) -> exact ordered labels
```

Leader output has one exact schema and contains no prose, score, confidence, or user-selected effect. Each validator independently reruns that mapping. A candidate is accepted only when its canonical ordered label vector exactly matches the validator's independently canonicalized vector. Model errors and malformed outputs force disagreement or transaction failure; they do not create state.

The constructor computes a conservative full-calibration prompt bound using the immutable rubric, labels, configured anchor count, maximum anchor identifiers, and maximum examples under worst-case JSON escaping. An over-budget configuration is rejected before any commitment can be stored. Runtime character/UTF-8 prompt checks and raw/canonical LLM-response caps remain independent defenses.

## State machine

```text
COMMITTING --all commitments/open_reveal--> REVEALING
COMMITTING --commit deadline expires------> DIVERGENT
REVEALING --reveal/calibration deadline expires--> DIVERGENT
REVEALING --calibrate by deadline/pass------------> ACTIVE
REVEALING --calibrate by deadline/fail------------> DIVERGENT
```

`ACTIVE` and `DIVERGENT` are terminal. There are no admin overrides, rubric edits, relabeling, retries, or upgrades. A different rubric or anchor set requires a new deployment.

## Calibration math

- `classified_count`: predictions not equal to `UNCLASSIFIED`.
- `correct_count`: predictions exactly equal to committed expected labels.
- `accuracy_bps = floor(correct_count * 10000 / expected_anchor_count)`.
- `coverage_bps = floor(classified_count * 10000 / expected_anchor_count)`.
- Every configured label must occur at least once among expected anchor labels.
- `ACTIVE` requires label coverage, minimum accuracy, and minimum classification coverage.

Accuracy deliberately uses every anchor as its denominator, so abstention cannot improve accuracy. Coverage separately prevents a model from passing by abstaining.

## Commitments and digests

Every commitment includes the policy domain, exact contract configuration digest, canonical anchor ID, canonical text, expected label, and 32-byte hexadecimal salt using length-framed Keccak-256 input. The configuration digest includes chain ID, contract address, controller, rubric, labels, thresholds, counts, deadlines, and policy version. The terminal digest commits to configuration, result, metrics, and the disclosed anchor outcome records.

Length framing prevents concatenation ambiguity. Contract and chain binding prevents cross-deployment replay. Commitment preimages must be computed with the local helper; there is deliberately no public contract preview method. A hosted RPC call is not an appropriate confidentiality boundary.

The expected labels are public after reveal, but `_classification_prompt` sends only the rubric, closed labels, anchor IDs, and example text to the model. Thus normal contract execution is prompt-blind to ground truth, not operator-blind. A protocol requiring cryptographic blindness from validator operators would need separate text and label commitments, prediction finalization before label reveal, and a later deterministic scoring phase.

## Deliberate distinction

QuestionZero asks whether a rule specification is adjudicable. A policy engine applies a policy to live cases. This contract does neither: it uses precommitted ground-truth anchor labels, omitted from the model prompt, to decide whether a fixed rubric is calibrated enough to be enabled elsewhere.
