import pytest
import pandas as pd
import logging
from src.decision_normaliser import DecisionNormaliser


@pytest.fixture
def droid_keep_blank_dispose_reason() -> pd.DataFrame:
    # test_file_01.txt is keep
    # test_file_02.txt is dispose, not reason
    df = pd.read_csv("tests\\data\\decision_normaliser\\Case_Keep_Decisions.csv")
    return df


@pytest.fixture
def droid_no_reason() -> pd.DataFrame:
    # test_file_01.txt is keep
    # test_file_02.txt is dispose, not reason
    df = pd.read_csv(
        "tests\\data\\decision_normaliser\\Case_Keep_Decisions.csv",
        usecols=[
            "ID",
            "PARENT_ID",
            "URI",
            "FILE_PATH",
            "NAME",
            "METHOD",
            "STATUS",
            "SIZE",
            "TYPE",
            "EXT",
            "LAST_MODIFIED",
            "EXTENSION_MISMATCH",
            "MD5_HASH",
            "FORMAT_COUNT",
            "PUID",
            "MIME_TYPE",
            "FORMAT_NAME",
            "FORMAT_VERSION",
            "DECISION",
        ],
    )
    return df


@pytest.fixture
def droid_no_decisions() -> pd.DataFrame:
    df = pd.read_csv("tests\\data\\decision_normaliser\\Case_No_Decisions.csv")
    return df


def test_fix_blank_disposal_decisions(droid_keep_blank_dispose_reason):
    normaliser = DecisionNormaliser()
    outcome = normaliser.fix_blank_dispose_decisions(droid_keep_blank_dispose_reason)
    disposal_reason = outcome[outcome["DECISION"] == "dispose"]
    disposal_reason = disposal_reason["REASON"].to_list()
    for reason in disposal_reason:
        assert reason == "Not selected."


def test_fix_blank_no_reason_works(droid_no_reason):
    normaliser = DecisionNormaliser()
    outcome = normaliser.fix_blank_dispose_decisions(droid_no_reason)
    disposal_reason = outcome[outcome["DECISION"] == "dispose"]
    disposal_reason = disposal_reason["REASON"].to_list()
    for reason in disposal_reason:
        assert reason == "Not selected."


def test_existing_dispose_reasons_not_changed(droid_no_reason):
    df = droid_no_reason
    df["REASON"] = "Duplicate"
    normaliser = DecisionNormaliser()
    outcome = normaliser.fix_blank_dispose_decisions(df)
    disposal_reason = outcome[outcome["DECISION"] == "dispose"]
    disposal_reason = disposal_reason["REASON"].to_list()
    for reason in disposal_reason:
        assert reason == "Duplicate"


def test_normalise_decision_text(droid_keep_blank_dispose_reason):
    normaliser = DecisionNormaliser()
    outcome = normaliser.replace_decision(
        droid_keep_blank_dispose_reason, "keep", "retain-state-collection"
    )
    keeps = outcome[outcome["DECISION"] == "keep"]
    retain_state_coll = outcome[outcome["DECISION"] == "retain-state-collection"]
    assert keeps.size == 0
    assert retain_state_coll.size > 1


def test_update_decision_reason():
    data = {"URI": ["test"], "DECISION": ["check"], "REASON": [""]}
    df = pd.DataFrame.from_dict(data)
    normaliser = DecisionNormaliser()
    df = normaliser.update_decision_reason(df, "check", "Not selected")
    reason_list = df["REASON"].to_list()
    assert reason_list[0] == "Not selected"


def test_update_decision_no_reason(droid_no_reason):
    normaliser = DecisionNormaliser()
    df = normaliser.update_decision_reason(droid_no_reason, "keep", "Updated")
    reason_list = df.loc[df["DECISION"] == "keep", "REASON"].to_list()
    assert reason_list[0] == "Updated"
