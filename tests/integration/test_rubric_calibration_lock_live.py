"""Hosted GenLayer semantic smoke test. Run explicitly; it performs real inference."""

import json
from pathlib import Path
import secrets
import time

import pytest
from gltest import get_contract_factory
from gltest.assertions import tx_execution_succeeded
from gltest.types import TransactionStatus
from gltest.utils import extract_contract_address

from scripts.commitment import compute_anchor_commitment


RUBRIC = (
    "Classify an issue as BUG when it describes existing behavior that is broken, incorrect, or failing. "
    "Classify it as FEATURE when it requests a new capability or enhancement that does not yet exist."
)
ANCHOR_SPECS = [
    ("ANCHOR-01", "Saving an existing document crashes the application every time.", "BUG"),
    ("ANCHOR-02", "Add a selectable dark color theme to the application.", "FEATURE"),
    ("ANCHOR-03", "Every valid password is rejected by the login form.", "BUG"),
]


def _ok(receipt):
    assert tx_execution_succeeded(receipt), json.dumps(receipt, indent=2, default=str)


@pytest.mark.semantic
def test_live_consensus_calibrates_clear_closed_rubric():
    now = int(time.time())
    anchors = [(*anchor, secrets.token_hex(32)) for anchor in ANCHOR_SPECS]
    path = Path(__file__).resolve().parents[2] / "contracts" / "RubricCalibrationLock.py"
    factory = get_contract_factory(contract_file_path=path)
    deployment = factory.deploy_contract_tx(
        args=[
            "ISSUE-TRIAGE-LIVE",
            "V1",
            RUBRIC,
            '["BUG","FEATURE"]',
            3,
            10000,
            10000,
            now + 6 * 60 * 60,
            now + 12 * 60 * 60,
        ],
        wait_transaction_status=TransactionStatus.FINALIZED,
    )
    _ok(deployment)
    contract = factory.build_contract(extract_contract_address(deployment))
    print(f"contract_address={contract.address}")

    policy = contract.get_policy(args=[]).call()
    assert policy["contract_version"] == "0.2.1"
    labels = json.loads(policy["labels_json"])
    for anchor_id, text, label, salt in anchors:
        commitment = compute_anchor_commitment(
            policy["config_digest"],
            anchor_id,
            text,
            label,
            salt,
            labels,
        )
        _ok(
            contract.commit_anchor(args=[anchor_id, commitment]).transact(
                wait_transaction_status=TransactionStatus.FINALIZED
            )
        )
    _ok(contract.open_reveal(args=[]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    for anchor in anchors:
        _ok(
            contract.reveal_anchor(args=list(anchor)).transact(
                wait_transaction_status=TransactionStatus.FINALIZED
            )
        )
    _ok(contract.calibrate(args=[]).transact(wait_transaction_status=TransactionStatus.FINALIZED))

    state = contract.get_calibration(args=[]).call()
    print("calibration=" + json.dumps(state, sort_keys=True, default=str))
    assert state["status"] == "ACTIVE"
    assert state["accuracy_bps"] == 10000
    assert state["coverage_bps"] == 10000
    assert len(state["terminal_digest"]) == 64
