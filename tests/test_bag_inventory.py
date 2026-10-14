import pytest
import pandas as pd
import os
from src.bag_inventory import *


@pytest.fixture
def valid_input_data(tmpdir) -> dict:
    folder = os.path.join(tmpdir, "folder")
    empty_folder = os.path.join(tmpdir, "emptyfolder")
    os.mkdir(folder)
    os.mkdir(empty_folder)
    retain_file = os.path.join(folder, "test.txt")
    dispose_file = os.path.join(folder, "test2.txt")
    for file in [retain_file, dispose_file]:
        with open(file, "w") as f:
            f.write("test")
    return {
        "URI": [
            f"file:{tmpdir}",
            f"file:{folder}",
            f"file:{empty_folder}",
            f"file:{retain_file}",
            f"file:{dispose_file}",
        ],
        "TYPE": ["Folder", "Folder", "Folder", "File", "File"],
        "DECISION": ["", "", "", "retain-state-collection", "dispose"],
        "REASON": ["", "", "", "", "Not selected"],
        "SYSTEM": ["", "", "", "ArchivesSpace", ""],
        "SYSTEM_ID": ["", "", "", "12345", ""],
    }


@pytest.fixture
def valid_input_with_iso(tmpdir) -> dict:
    folder = os.path.join(tmpdir, "folder")
    empty_folder = os.path.join(tmpdir, "emptyfolder")
    os.mkdir(folder)
    os.mkdir(empty_folder)
    retain_file = os.path.join(folder, "test.iso")
    dispose_file = os.path.join(folder, "test2.txt")
    for file in [retain_file, dispose_file]:
        with open(file, "w") as f:
            f.write("test")
    return {
        "URI": [
            f"file:{tmpdir}",
            f"file:{folder}",
            f"file:{empty_folder}",
            f"file:{retain_file}",
            f"iso:file:{retain_file}!/internalfile.txt",
            f"file:{dispose_file}",
        ],
        "TYPE": ["Folder", "Folder", "Folder", "Container", "File", "File"],
        "DECISION": [
            "",
            "",
            "",
            "retain-state-collection",
            "retain-state-collection",
            "dispose",
        ],
        "REASON": ["", "", "", "", "", "Not selected"],
        "SYSTEM": ["", "", "", "ArchivesSpace", "", ""],
        "SYSTEM_ID": ["", "", "", "12345", "", ""],
    }


@pytest.fixture
def valid_bag_inventory(valid_input_data) -> BagInventory:
    df = pd.DataFrame.from_dict(valid_input_data)
    bi = BagInventory(df, "data\\")
    return bi


@pytest.fixture
def invalid_bag_inventory(valid_input_data) -> BagInventory:
    invalid_data = valid_input_data
    # no reason for dispose decision
    invalid_data["REASON"][4] = ""
    df = pd.DataFrame.from_dict(invalid_data)
    bi = BagInventory(df, "data\\")
    return bi


@pytest.fixture
def invalid_bag_inventory_ark_against_not_state_collection(
    valid_input_data, tmpdir
) -> BagInventory:
    valid_input_data["URI"].append(f"file:{tmpdir}\\folder\\text3.txt")
    valid_input_data["TYPE"].append("File")
    valid_input_data["DECISION"].append("retain-record")
    valid_input_data["REASON"].append("Not selected")
    valid_input_data["SYSTEM"].append("ArchivesSpace")
    valid_input_data["SYSTEM_ID"].append("12345")
    df = pd.DataFrame.from_dict(valid_input_data)
    bi = BagInventory(df, "data\\")
    return bi


@pytest.fixture
def valid_bag_inventory_with_check(valid_input_data, tmpdir) -> BagInventory:
    valid_input_data["URI"].append(f"file:{tmpdir}\\folder\\text3.txt")
    valid_input_data["TYPE"].append("File")
    valid_input_data["DECISION"].append("check")
    valid_input_data["REASON"].append("Not described")
    valid_input_data["SYSTEM"].append("")
    valid_input_data["SYSTEM_ID"].append("")
    df = pd.DataFrame.from_dict(valid_input_data)
    bi = BagInventory(df, "data\\")
    return bi


@pytest.fixture
def valid_bag_inventory_two_files_same_id(valid_input_data, tmpdir) -> BagInventory:
    valid_input_data["URI"].append(f"file:{tmpdir}\\folder\\text3.txt")
    valid_input_data["TYPE"].append("File")
    valid_input_data["DECISION"].append("retain-state-collection")
    valid_input_data["REASON"].append("")
    valid_input_data["SYSTEM"].append("ArchivesSpace")
    valid_input_data["SYSTEM_ID"].append("12345")
    df = pd.DataFrame.from_dict(valid_input_data)
    bi = BagInventory(df, "data\\")
    return bi


@pytest.fixture
def basic_decision_dict():
    return {
        "retain-state-collection": [{"files": ["data\\folder\\test.txt"]}],
        "retain-record": [],
        "dispose": [
            {"reason-text": "Not selected", "files": ["data\\folder\\test2.txt"]}
        ],
    }


@pytest.fixture
def basic_description_dict():
    return {"archivesspace": {"12345": ["data\\folder\\test.txt"]}}


@pytest.fixture
def valid_bag_no_description(valid_input_data) -> BagInventory:
    valid_input_data.pop("SYSTEM")
    valid_input_data.pop("SYSTEM_ID")
    df = pd.DataFrame.from_dict(valid_input_data)
    bi = BagInventory(df, "data\\")
    return bi


def test_get_inventory_metadata(valid_bag_inventory: BagInventory):
    metadata = valid_bag_inventory.get_inventory_metadata("creator", "testing")
    fields = [*metadata]
    expected_fields = [
        "time",
        "created_by",
        "process",
        "platform",
        "script",
        "python_version",
        "file_count",
        "folder_count",
        "has_archive_files",
    ]
    expected_fields.sort()
    fields.sort()
    assert fields == expected_fields
    assert metadata.get("created_by") == "creator"
    assert metadata.get("process") == "testing"


def test_get_decision_dict(valid_bag_inventory, basic_decision_dict):
    output = valid_bag_inventory.get_decision_inventory()

    assert output.keys() == basic_decision_dict.keys()
    assert output == basic_decision_dict


def test_get_decision_dict_no_description(
    valid_bag_no_description, basic_decision_dict
):
    output = valid_bag_no_description.get_decision_inventory()
    assert output.keys() == basic_decision_dict.keys()
    assert output == basic_decision_dict


def test_get_decision_with_check(valid_bag_inventory_with_check, basic_decision_dict):
    expected = {
        "check": [
            {"reason-text": "Not described", "files": ["data\\folder\\text3.txt"]}
        ]
    }
    basic_decision_dict.update(expected)
    output = valid_bag_inventory_with_check.get_decision_inventory()
    assert output.keys() == basic_decision_dict.keys()
    assert output == basic_decision_dict


def test_get_description_dict(valid_bag_inventory, basic_description_dict):
    outcome = valid_bag_inventory.get_description_inventory()
    assert outcome.keys() == basic_description_dict.keys()
    assert outcome == basic_description_dict


def test_get_description_no_description_returns_none(valid_bag_no_description):
    outcome = valid_bag_no_description.get_description_inventory()
    assert outcome == None


# if files are not retain they must have a reason
def test_get_decision_no_reason_is_invalid(invalid_bag_inventory):
    is_valid = invalid_bag_inventory.validate()
    assert is_valid == False


def test_valid_inventory_is_valid(valid_bag_inventory):
    is_valid = valid_bag_inventory.validate()
    assert is_valid == True


# if description is present it must have a type of retain-state-collection
@pytest.mark.parametrize(
    "system, system_id",
    [
        ("ArchivesSpace", ""),
        ("", "ARK:99999/9999"),
    ],
)
def test_uneven_system_system_id_is_invalid(valid_input_data, system, system_id):
    valid_input_data["SYSTEM"][3] = system
    valid_input_data["SYSTEM_ID"][3] = system_id
    df = pd.DataFrame.from_dict(valid_input_data)
    bi = BagInventory(df, "data\\")
    is_valid = bi.validate()
    assert is_valid == False


@pytest.mark.parametrize(
    "system, system_id",
    [
        ("ArchivesSpace", ""),
        ("", "ARK:99999/9999"),
    ],
)
def test_uneven_system_system_id_is_ignored_for_iso(
    valid_input_with_iso, system, system_id
):
    data = valid_input_with_iso
    data["SYSTEM"][4] = system
    data["SYSTEM_ID"][4] = system_id
    df = pd.DataFrame.from_dict(data)
    bi = BagInventory(df, "data\\")
    is_valid = bi.validate()
    assert is_valid == True


@pytest.mark.parametrize(
    "decision",
    [("dispose"), (""), ("retain-record"), ("check"), (None)],
)
def test_wrong_decsion_with_description_is_invalid(valid_input_data, decision):
    valid_input_data["DECISION"][3] = decision
    df = pd.DataFrame.from_dict(valid_input_data)
    bi = BagInventory(df, "data\\")
    is_valid = bi.validate()
    assert is_valid == False


def test_folders_missing_decisions_are_valid(valid_bag_inventory):
    is_valid = valid_bag_inventory.validate()
    assert is_valid == True


def test_not_state_collection_with_description_id_is_invalid(
    invalid_bag_inventory_ark_against_not_state_collection,
):
    is_valid = invalid_bag_inventory_ark_against_not_state_collection.validate()
    assert is_valid == False


## containerised file handling (iso/zip)
