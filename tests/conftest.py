import pytest
import os
import pandas as pd


@pytest.fixture
def SC_transfer_1():
    cwd = os.getcwd()
    path = os.path.join(cwd, "tests", "test_data", "Archive", "SC99999", "t1")
    return os.path.normpath(path)


@pytest.fixture
def report_for_transfer_1():
    path = os.path.join("tests", "test_data", "droid_reports", "SC99999_t1_DROID.csv")
    df = pd.read_csv(path)
    return df


@pytest.fixture
def report_for_transfer_1_multiple_arks():
    path = os.path.join("tests", "test_data", "droid_reports", "SC99999_t1_DROID.csv")
    df = pd.read_csv(path)
    df["DECISION"] = "retain-state-collection"
    df["REASON"] = ""
    df["SYSTEM"] = "archivesspace"
    df["SYSTEM_ID"] = "1"
    indexes = df.index.to_list()
    indexes = [f"ark:/99999/{x+1}" for x in indexes]
    df["SYSTEM_ID"] = indexes
    return df


@pytest.fixture
def report_for_transfer_1_one_ark():
    path = os.path.join("tests", "test_data", "droid_reports", "SC99999_t1_DROID.csv")
    df = pd.read_csv(path)
    df["DECISION"] = "retain-state-collection"
    df["REASON"] = ""
    df["SYSTEM"] = "archivesspace"
    df["SYSTEM_ID"] = "1"
    df["SYSTEM_ID"] = "ark:/99999/123"
    return df
