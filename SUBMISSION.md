# Portal submission

Current-source StudioNet evidence is captured below. Replace GitHub and Bradbury placeholders only with frozen-source evidence before submission; Bradbury is not yet claimed.

**Title**

```text
Rubric Calibration Lock — Reusable Intelligent Contract
```

**Notes / Description**

```text
Built an MIT-licensed Rubric Calibration Lock, a reusable GenLayer contract that prevents a natural-language rubric from activating until committed anchors pass calibration. The deployer fixes labels, thresholds, anchor count, and deadlines; a local utility computes domain-separated commitments without exposing preimages to hosted RPC. After reveal, leader and validators independently classify each anchor into one allowed label or UNCLASSIFIED. Deterministic code computes accuracy and coverage, then locks ACTIVE or DIVERGENT. Prompt budgets cover all anchors and worst-case JSON escaping; LLM responses are capped. Includes 76 direct tests and 2 five-validator mocked GLSim tests. A no-mock StudioNet lifecycle deployed byte-identical source at 0xD0E7AD1037500E9EFF26A711Fa09075E2d545674, finalized all 9 writes, and returned ACTIVE with 3/3 correct and classified anchors at 10000 bps accuracy and coverage. It calibrates a rubric; it does not evaluate production inputs.
```

**Evidence entries**

```text
GitHub Repository
CURRENT_SOURCE_GITHUB_REPOSITORY_URL_PENDING

GitHub File — exact contract source
CURRENT_SOURCE_GITHUB_CONTRACT_SOURCE_URL_PENDING

GitHub File — testing evidence
CURRENT_SOURCE_GITHUB_TESTING_URL_PENDING

GenLayer Explorer Contract
CURRENT_SOURCE_BRADBURY_EXPLORER_URL_PENDING

GenLayer StudioNet Contract Address
0xD0E7AD1037500E9EFF26A711Fa09075E2d545674

GitHub File — finalized StudioNet deployment proof
CURRENT_SOURCE_PUBLIC_REPOSITORY_URL_PENDING/blob/main/deployments/studionet-2026-08-12-current-proof.json
```

Submit under **Intelligent Contracts**. Replace every placeholder, use the actual contribution date, and report only finalized, independently checked results. The StudioNet harness retained no transaction hashes or receipts and exposed no validator identities, votes, vote count, or model names; do not claim them. Add finalized Bradbury evidence before claiming Bradbury.
