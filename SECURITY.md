# Security

## Protected properties

- Immutable rubric, label set, thresholds, anchor count, controller, and deadlines.
- Controller-only commit, phase transition, reveal, and calibration calls.
- Permissionless expiry only after objective deadlines, with late calibration rejected deterministically.
- Unique anchor IDs and commitments; no reveal replay or terminal retry.
- Commitment binding to canonical text, label, salt, configuration, contract, and chain.
- Exact LLM response schema, exact anchor order, closed labels, and no free-form explanation.
- Independent validator classification rather than schema-only approval.
- Input character and UTF-8 byte limits, collection bounds, Unicode/control-character filtering, conservative aggregate prompt budgeting with worst-case JSON escaping, runtime prompt limits, raw/canonical LLM response limits, and calibration-window bounds.
- All write methods reject transferred native value.

## Prompt injection

Rubric and anchor content is explicitly delimited as untrusted quoted data. The parser rejects extra output fields, unknown labels, missing/duplicate/reordered classifications, oversized responses, and malformed JSON. These controls confine the accepted output schema; they do not make an LLM immune to prompt injection or semantic manipulation. Validator diversity and an adversarial anchor set are therefore necessary, not optional.

## Commitment confidentiality

The contract has no public commitment-preview method. Use `scripts/commitment.py` inside a trusted local process with a fresh `secrets.token_hex(32)` value per anchor. Sending a preimage to a hosted RPC, putting it in a URL or command-line argument, reusing a salt, or choosing a guessable salt weakens confidentiality. The contract validates a salt's 32-byte hexadecimal shape but cannot prove entropy.

## Threats not solved

- A controller can choose weak, biased, leaked, duplicated, or unrepresentative anchors.
- Commit/reveal hides labels only until reveal; all revealed material is public.
- Expected labels are excluded from the model prompt but remain visible to validator operators after reveal; this is not a cryptographically blind evaluation protocol.
- A passing calibration does not guarantee future model or provider behavior.
- Correlated model failures can pass decentralized consensus.
- Exact-label consensus may reduce liveness on genuinely ambiguous anchors. Use `UNCLASSIFIED`, clearer rubrics, or a new deployment; do not weaken comparison after deployment.
- The contract does not bind itself to a downstream evaluator's code. Consumers must pin the deployment and configuration digest and separately audit that evaluator.
- Transaction finality and appeals remain network-level concerns.

## Deployment checklist

1. Use only the pinned runner header in the source.
2. Use a fresh testnet-only key and verify chain ID and contract address.
3. Generate cryptographically random 32-byte salts off-chain; never reuse them or send preimages through a hosted preview call.
4. Include clear positive, negative, boundary, ambiguous, and injection anchors for every label.
5. Keep the anchor set secret until commitments finalize.
6. Verify all reveals and the terminal digest in the explorer.
7. Run heterogeneous real-validator testing before high-consequence use.

## Reporting

Open a private security advisory in the repository. Do not include private keys, unrevealed anchors, or reusable salts in a public issue.
