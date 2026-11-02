import pytest
import os
import pandas as pd

COMMON_BAG_UUID = "8be4df61-93ca-11d2-aa0d-00e098032b8c"


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
def SC_transfer_2():
    cwd = os.getcwd()
    path = os.path.join(cwd, "tests", "test_data", "Archive", "SC99999", "t2")
    return os.path.normpath(path)


@pytest.fixture
def report_for_transfer_2():
    path = os.path.join("tests", "test_data", "droid_reports", "SC99999_t2_DROID.csv")
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
    df["SYSTEM_ID"] = "ark:/99999/123"
    return df


@pytest.fixture
def report_for_transfer_2_one_id():
    path = os.path.join("tests", "test_data", "droid_reports", "SC99999_t2_DROID.csv")
    df = pd.read_csv(path)
    df["DECISION"] = "retain-state-collection"
    df["REASON"] = ""
    df["SYSTEM"] = "alma"
    df["SYSTEM_ID"] = "9900007636"
    return df


@pytest.fixture
def validation_df():
    data = {
        "OutcomeIdentifier": [1],
        "BagUUID": [COMMON_BAG_UUID],
        "Outcome": ["Pass"],
        "Errors": [""],
        "BagPath": ["\\\\path.location\\identifier\\t1"],
        "StartTime": ["2025-07-08 10:20:38.380232"],
        "EndTime": ["2025-07-08 10:21:38.380232"],
    }
    df = pd.DataFrame.from_dict(data)
    return df


@pytest.fixture
def big_validation_df():
    data = {
        "OutcomeIdentifier": [1, 2, 3, 4, 5],
        "BagUUID": [
            COMMON_BAG_UUID,
            COMMON_BAG_UUID,
            "8be4df61-93ca-11d2-aa0d-00e098032b8d",
            "f4ac41a5-49ef-4cbb-9aa1-e3935efd8ec0",
            "7fc12852-05ff-4405-abef-459d24aaa6aa",
        ],
        "Outcome": ["Pass", "Pass", "Pass", "Pass", "Pass"],
        "Errors": ["", "", "", "", ""],
        "BagPath": [
            "\\\\path.location\\identifier\\t1",
            "\\\\path.location\\identifier\\t1",
            "\\\\path.location\\identifier\\t1",
            os.path.join(os.getcwd(), "test_data", "Archive", "SC99999", "t1"),
            os.path.join(os.getcwd(), "test_data", "Archive", "SC99999", "t2"),
        ],
        "StartTime": [
            "2025-07-08 10:20:38.380232",
            "2025-07-09 10:20:38.380232",
            "2025-07-10 10:20:38.380232",
            "2025-07-10 10:20:38.380232",
            "2025-07-11 10:20:38.380232",
        ],
        "EndTime": [
            "2025-07-08 10:21:38.380232",
            "2025-07-09 10:21:38.380232",
            "2025-07-10 10:21:38.380232",
            "2025-07-10 10:21:38.380232",
            "2025-07-11 10:21:38.380232",
        ],
    }
    df = pd.DataFrame.from_dict(data)
    return df


@pytest.fixture
def transfer_df():
    data = {
        "TransferID": [603, 604, 605],
        "TransferDate": ["2026-09-10", "2026-10-14", "2026-10-14"],
        "BagDate": ["2026-09-10", "2026-10-14", "2026-10-14"],
        "CollectionIdentifier": ["ID-999-999", "SC99999", "SC99999"],
        "OutcomeFolderTitle": ["ID-999-999\\t2", "SC99999\\t1", "SC99999\\t2"],
        "OriginalFolderTitle": [
            "ID-999-999_TestTransfer_20260910",
            "SC99999_An_example_sip_20240430",
            "SC99999_A_sip_with_hierarchy_20240430",
        ],
        "TransferTimeSeconds": ["952.262885", "2.0123", "12.343"],
        "ContactName": ["JDoe", "SBourke", "SBourke"],
        "SourceOrganisation": [
            "State Library Victoria",
            "State Library Victoria",
            "State Library Victoria",
        ],
        "BagUUID": [
            COMMON_BAG_UUID,
            "f4ac41a5-49ef-4cbb-9aa1-e3935efd8ec0",
            "7fc12852-05ff-4405-abef-459d24aaa6aa",
        ],
        "PayloadOxum": ["22517139535.207", "0.4", "0.6"],
        "ManifestSHA256Hash": [
            "4b0afa46da6626d9258aacfe639aa9670bd7a06083e70f950ba64f50cf6ab4b7",
            "4b0afa46da6626d9258aacfe639aa9670bd7a06083e70f950ba64f50cf699999",
            "4b0afa46da6626d9258aacfe639aa9670bd712343e70f950ba64f50cf699999",
        ],
        "StartTime": [
            "2026-09-10 08:43:54.470389",
            "2026-09-10 08:01:00.1234",
            "2026-09-11 08:01:00.1234",
        ],
        "EndTime": [
            "2026-09-10 08:59:46.733274",
            "2026-09-10 08:01:02.1234",
            "2026-09-11 08:01:02.1234",
        ],
    }
    df = pd.DataFrame.from_dict(data)
    return df
