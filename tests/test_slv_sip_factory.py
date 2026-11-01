import pytest
import os
from src.slv_sip_factory import (
    ConcreteEventCreator,
    SlvSipFactory,
)
import pandas as pd
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


def test_slv_sip_factory_compiles_events(transfer_df, big_validation_df):
    factory = SlvSipFactory(validation_df=big_validation_df, transfer_df=transfer_df)
    events = factory.compile_events(COMMON_BAG_UUID)
    assert len(events) == 4


def test_slv_sip_factory_creates_sips_from_json_multi_ark(
    report_for_transfer_1_multiple_arks,
    SC_transfer_1,
    tmp_path,
    transfer_df,
    big_validation_df,
):
    uuid = "f4ac41a5-49ef-4cbb-9aa1-e3935efd8ec0"
    factory = SlvSipFactory(validation_df=big_validation_df, transfer_df=transfer_df)
    output_dir = tmp_path / "folder"
    output_dir.mkdir()
    print(output_dir)
    factory.build_sip_from_json(
        bag_uuid=uuid,
        input_dir=SC_transfer_1,
        output_dir=output_dir,
        sip_title="test-sip",
        transfer_manifest=report_for_transfer_1_multiple_arks,
    )
    transfer_count = len(os.listdir(output_dir))
    assert transfer_count == 4


def test_slv_sip_factory_creates_sip_from_json(
    report_for_transfer_1_one_ark,
    SC_transfer_1,
    tmp_path,
    transfer_df,
    big_validation_df,
):
    uuid = "f4ac41a5-49ef-4cbb-9aa1-e3935efd8ec0"
    factory = SlvSipFactory(validation_df=big_validation_df, transfer_df=transfer_df)
    output_dir = tmp_path / "folder"
    output_dir.mkdir()
    factory.build_sip_from_json(
        bag_uuid=uuid,
        input_dir=SC_transfer_1,
        output_dir=output_dir,
        sip_title="test-sip",
        transfer_manifest=report_for_transfer_1_one_ark,
    )
    transfer_count = len(os.listdir(output_dir))
    assert transfer_count == 1
