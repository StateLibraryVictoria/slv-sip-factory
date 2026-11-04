from src.event_handlers import ConcreteEventCreator
from conftest import COMMON_BAG_UUID


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
