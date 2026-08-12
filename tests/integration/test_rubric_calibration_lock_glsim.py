"""Five-validator GLSim consensus coverage for RubricCalibrationLock."""

import json
from pathlib import Path
import time

from gltest import get_contract_factory, get_validator_factory
from gltest.assertions import tx_execution_failed, tx_execution_succeeded
from gltest.types import TransactionStatus
from gltest.utils import extract_contract_address

from scripts.commitment import compute_anchor_commitment


RUBRIC = (
    "Classify an issue as BUG when it describes existing behavior that is broken, incorrect, or failing. "
    "Classify it as FEATURE when it requests a new capability or enhancement that does not yet exist."
)
ANCHORS = [
    ("ANCHOR-01", "Saving an existing document crashes the application every time.", "BUG", "a" * 64),
    ("ANCHOR-02", "Add a selectable dark color theme to the application.", "FEATURE", "b" * 64),
    ("ANCHOR-03", "Every valid password is rejected by the login form.", "BUG", "c" * 64),
]
PASS_RESULT = json.dumps(
    {
        "classifications": [
            {"anchor_id": anchor_id, "label": label}
            for anchor_id, _, label, _ in ANCHORS
        ]
    },
    separators=(",", ":"),
)
PROMPT_KEY = "consensus-critical CALIBRATION classification"


def _receipt_dump(receipt):
    return json.dumps(receipt, indent=2, sort_keys=True, default=str)


def _validator_context(response=PASS_RESULT):
    validators = get_validator_factory().batch_create_mock_validators(
        5,
        mock_llm_response={"nondet_exec_prompt": {PROMPT_KEY: response}},
    )
    return {"validators": [validator.to_dict() for validator in validators]}


def _deploy():
    now = int(time.time())
    path = Path(__file__).resolve().parents[2] / "contracts" / "RubricCalibrationLock.py"
    factory = get_contract_factory(contract_file_path=path)
    receipt = factory.deploy_contract_tx(
        args=[
            "ISSUE-TRIAGE",
            "V1",
            RUBRIC,
            '["BUG","FEATURE"]',
            3,
            10000,
            10000,
            now + 3600,
            now + 7200,
        ],
        wait_transaction_status=TransactionStatus.FINALIZED,
    )
    assert tx_execution_succeeded(receipt), _receipt_dump(receipt)
    return factory.build_contract(extract_contract_address(receipt))


def _succeed(receipt):
    assert tx_execution_succeeded(receipt), _receipt_dump(receipt)


def _prepare(contract):
    policy = contract.get_policy(args=[]).call()
    labels = json.loads(policy["labels_json"])
    for anchor_id, text, label, salt in ANCHORS:
        commitment = compute_anchor_commitment(
            policy["config_digest"],
            anchor_id,
            text,
            label,
            salt,
            labels,
        )
        receipt = contract.commit_anchor(args=[anchor_id, commitment]).transact(
            wait_transaction_status=TransactionStatus.FINALIZED
        )
        _succeed(receipt)
    _succeed(
        contract.open_reveal(args=[]).transact(
            wait_transaction_status=TransactionStatus.FINALIZED
        )
    )
    for row in ANCHORS:
        _succeed(
            contract.reveal_anchor(args=list(row)).transact(
                wait_transaction_status=TransactionStatus.FINALIZED
            )
        )


def test_five_validator_consensus_locks_active_rubric():
    contract = _deploy()
    _prepare(contract)
    receipt = contract.calibrate(args=[]).transact(
        transaction_context=_validator_context(),
        wait_transaction_status=TransactionStatus.FINALIZED,
    )
    _succeed(receipt)
    state = contract.get_calibration(args=[]).call()
    policy = contract.get_policy(args=[]).call()
    assert state["status"] == "ACTIVE"
    assert state["reason_code"] == "CALIBRATION_THRESHOLDS_MET"
    assert state["correct_count"] == 3
    assert state["accuracy_bps"] == 10000
    assert state["coverage_bps"] == 10000
    assert policy["controller"].startswith("0x")
    assert contract.is_active(args=[policy["config_digest"]]).call() is True
    assert len(state["terminal_digest"]) == 64


def test_five_validator_malformed_output_fails_without_state_change():
    contract = _deploy()
    _prepare(contract)
    receipt = contract.calibrate(args=[]).transact(
        transaction_context=_validator_context('{"classifications":[]}'),
        wait_transaction_status=TransactionStatus.FINALIZED,
    )
    assert tx_execution_failed(receipt), _receipt_dump(receipt)
    state = contract.get_calibration(args=[]).call()
    assert state["status"] == "REVEALING"
    assert state["terminal_digest"] == ""
