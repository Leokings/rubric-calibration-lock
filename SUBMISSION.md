# Portal submission

Current-source StudioNet and Bradbury evidence is finalized. The GitHub repository is private until submission; make it public before Portal reviewers evaluate these links.

**Contribution Date**

```text
08/12/2026
```

**Title**

```text
Rubric Calibration Lock - Reusable Intelligent Contract
```

**Notes / Description**

```text
Built an MIT-licensed Rubric Calibration Lock, a reusable GenLayer IC that prevents a natural-language rubric from activating until committed anchors pass calibration. The deployer fixes labels, thresholds, anchor count and deadlines; a local tool computes domain-separated commitments without sending preimages to hosted RPC. After reveal, leader and validators independently classify each anchor into an allowed label or UNCLASSIFIED. Deterministic code computes accuracy and coverage, then irreversibly locks ACTIVE or DIVERGENT. Prompt budgets cover anchors and worst-case JSON escaping; LLM outputs are capped and schema-bound. Includes 77 direct tests and 2/2 five-validator mocked GLSim tests. Byte-exact v0.2.1 passed no-mock StudioNet and finalized on Bradbury at 0x4e4a0a7d9b46089740fa22A1881230753f13c106; its 8-write lifecycle finalized with 5/5 agreement and ACTIVE, 3/3 correct/classified, 10000 bps accuracy/coverage. It calibrates a rubric; it does not evaluate production inputs.
```

**Evidence entries**

```text
GitHub Repository
https://github.com/Leokings/rubric-calibration-lock

GitHub File - exact contract source
https://github.com/Leokings/rubric-calibration-lock/blob/main/contracts/RubricCalibrationLock.py

GitHub File - testing evidence
https://github.com/Leokings/rubric-calibration-lock/blob/main/TEST_RESULTS.md

GenLayer Explorer Contract
https://explorer-bradbury.genlayer.com/address/0x4e4a0a7d9b46089740fa22A1881230753f13c106

GenLayer StudioNet Contract Address
0xC914Af58d5576dF91898B1AF9ef231B8e65364ca

GitHub File - finalized StudioNet deployment proof
https://github.com/Leokings/rubric-calibration-lock/blob/main/deployments/studionet-2026-08-12-v0.2.1-current-proof.json

GitHub File - finalized Bradbury deployment and smoke proof
https://github.com/Leokings/rubric-calibration-lock/blob/main/deployments/bradbury-2026-08-12-v0.2.1-current-proof.json
```

Submit under **Intelligent Contracts**. The StudioNet harness retained no transaction hashes or receipts and exposed no validator identities, votes, vote count, or model names; do not claim them. Bradbury exposed transaction/vote counts but not validator model/provider identities, so do not claim heterogeneous-model execution.
