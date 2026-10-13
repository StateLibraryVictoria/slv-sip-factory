import pytest
from src.slv_sip_factory import ConcreteValidationEventCreator
import pandas as pd


@pytest.fixture
def validation_df():
    data = {
        "OutcomeIdentifier": [1],
        "BagUUID": ["8be4df61-93ca-11d2-aa0d-00e098032b8c"],
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
            "8be4df61-93ca-11d2-aa0d-00e098032b8c",
            "8be4df61-93ca-11d2-aa0d-00e098032b8c",
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


def test_validation_event_creator(validation_df):
    creator = ConcreteValidationEventCreator()
    validation_event = creator.build_events(
        "8be4df61-93ca-11d2-aa0d-00e098032b8c", validation_df
    )
    events = validation_event.parse_events()
    event = events[0]
    assert event.get("eventType") == "PRE-DEPOSIT"
    assert event.get("eventIdentifierValue") == "1"
    assert (
        event.get("eventDescription")
        == "Bag integrity validated at path '\\\\path.location\\identifier\\t1'"
    )
    assert event.get("eventDateTime") == "2025-07-08 10:21:38.380232"


def test_validation_event_creator_two_events(big_validation_df):
    creator = ConcreteValidationEventCreator()
    validation_event = creator.build_events(
        "8be4df61-93ca-11d2-aa0d-00e098032b8c", big_validation_df
    )
    events = validation_event.parse_events()
    assert len(events) == 2
    event = events[1]
    assert event.get("eventType") == "PRE-DEPOSIT"
    assert event.get("eventIdentifierValue") == "2"
    assert (
        event.get("eventDescription")
        == "Bag integrity validated at path '\\\\path.location\\identifier\\t1'"
    )
    assert event.get("eventDateTime") == "2025-07-09 10:21:38.380232"
