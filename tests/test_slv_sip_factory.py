import pytest
from src.slv_sip_factory import (
    ConcreteEventCreator,
    SlvSipFactory,
)
import pandas as pd

COMMON_BAG_UUID = "8be4df61-93ca-11d2-aa0d-00e098032b8c"


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
        "OutcomeIdentifier": [1, 2, 3],
        "BagUUID": [
            COMMON_BAG_UUID,
            COMMON_BAG_UUID,
            "8be4df61-93ca-11d2-aa0d-00e098032b8d",
        ],
        "Outcome": ["Pass", "Pass", "Pass"],
        "Errors": ["", "", ""],
        "BagPath": [
            "\\\\path.location\\identifier\\t1",
            "\\\\path.location\\identifier\\t1",
            "\\\\path.location\\identifier\\t1",
        ],
        "StartTime": [
            "2025-07-08 10:20:38.380232",
            "2025-07-09 10:20:38.380232",
            "2025-07-10 10:20:38.380232",
        ],
        "EndTime": [
            "2025-07-08 10:21:38.380232",
            "2025-07-09 10:21:38.380232",
            "2025-07-10 10:21:38.380232",
        ],
    }
    df = pd.DataFrame.from_dict(data)
    return df


@pytest.fixture
def transfer_df():
    data = {
        "TransferID": [603],
        "TransferDate": ["2026-09-10"],
        "BagDate": ["2026-09-10"],
        "CollectionIdentifier": ["ID-999-999"],
        "Size": ["20.971 GiB"],
        "FileCount": ["207"],
        "OutcomeFolderTitle": ["ID-999-999\\t2"],
        "OriginalFolderTitle": ["ID-999-999_TestTransfer_20260910"],
        "TransferTimeSeconds": ["952.262885"],
        "ContactName": ["JDoe"],
        "SourceOrganisation": ["State Library Victoria"],
        "BagUUID": [COMMON_BAG_UUID],
        "PayloadOxum": ["22517139535.207"],
        "ManifestSHA256Hash": [
            "4b0afa46da6626d9258aacfe639aa9670bd7a06083e70f950ba64f50cf6ab4b7"
        ],
        "StartTime": ["2026-09-10 08:43:54.470389"],
        "EndTime": ["2026-09-10 08:59:46.733274"],
        "Bytes": ["22517139535"],
    }
    df = pd.DataFrame.from_dict(data)
    return df


def test_validation_event_creator(validation_df):
    creator = ConcreteEventCreator()
    events = creator.build_events("validation", COMMON_BAG_UUID, validation_df)
    event = events[0]
    assert event.get("eventType") == "PRE-DEPOSIT"
    assert event.get("eventIdentifierValue") == "1"
    assert (
        event.get("eventDescription")
        == "Bag integrity validated at path '\\\\path.location\\identifier\\t1' by bagit.py <https://github.com/LibraryOfCongress/bagit-python>"
    )
    assert event.get("eventDateTime") == "2025-07-08 10:21:38.380232"
    assert event.get("eventOutcome1") == "Success"


def test_validation_event_creator_two_events(big_validation_df):
    creator = ConcreteEventCreator()
    events = creator.build_events("validation", COMMON_BAG_UUID, big_validation_df)
    assert len(events) == 2
    event = events[1]
    assert event.get("eventType") == "PRE-DEPOSIT"
    assert event.get("eventIdentifierValue") == "2"
    assert (
        event.get("eventDescription")
        == "Bag integrity validated at path '\\\\path.location\\identifier\\t1' by bagit.py <https://github.com/LibraryOfCongress/bagit-python>"
    )
    assert event.get("eventDateTime") == "2025-07-09 10:21:38.380232"


def test_transfer_event_creator(transfer_df):
    creator = ConcreteEventCreator()
    events = creator.build_events("transfer", COMMON_BAG_UUID, transfer_df)
    event = events[0]
    assert event.get("eventType") == "PRE-DEPOSIT"
    assert event.get("eventIdentifierValue") == "603"
    assert event.get("eventDescription") == "Transferred to statecollectionstore."
    assert event.get("eventDateTime") == "2026-09-10 08:59:46.733274"
    assert (
        event.get("eventOutcomeDetail1")
        == r"Files: 207, bytes: 22517139535, transferred by: JDoe, with collection id: ID-999-999. Resulted in folder: ID-999-999\t2. Transfer completed using: bagit.py <https://github.com/LibraryOfCongress/bagit-python>"
    )


def test_slv_sip_factory_compiles_events(transfer_df, big_validation_df):
    factory = SlvSipFactory(validation_df=big_validation_df, transfer_df=transfer_df)
    events = factory.compile_events(COMMON_BAG_UUID)
    assert len(events) == 4
