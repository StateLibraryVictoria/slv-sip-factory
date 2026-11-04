from src.sip_json_factory import JsonInventory
import json
import os
import pytest


@pytest.fixture
def json_inventory(report_for_transfer_1_multiple_arks, SC_transfer_1):
    j = JsonInventory(report_for_transfer_1_multiple_arks, root_dir=SC_transfer_1)
    return j


def test_load_bag_info(SC_transfer_1, report_for_transfer_1):
    j = JsonInventory(report_for_transfer_1, root_dir=SC_transfer_1)
    bag_info = j.load_bag_info()
    bag_uuid = bag_info.get("Internal-Sender-Identifier")
    assert bag_uuid == ["f4ac41a5-49ef-4cbb-9aa1-e3935efd8ec0"]


def test_load_file_hashes(SC_transfer_1, report_for_transfer_1):
    j = JsonInventory(report_for_transfer_1, root_dir=SC_transfer_1)
    files = j.load_file_checksums()
    print(files)
    example = files.get("\\😂😂😂.msg")
    assert example == "d41d8cd98f00b204e9800998ecf8427e"


def test_build_json_fails_with_no_system_info(SC_transfer_1, report_for_transfer_1):
    j = JsonInventory(report_for_transfer_1, root_dir=SC_transfer_1)
    with pytest.raises(ValueError) as e_info:
        j.build_rosetta_json()


def test_update_rosetta_paths_has_expected_columns(
    SC_transfer_1, report_for_transfer_1_one_ark
):
    j = JsonInventory(report_for_transfer_1_one_ark, root_dir=SC_transfer_1)
    df = j.update_rosetta_paths(j.df)
    df = j.get_file_information(df)
    expected_columns = [
        "physical_path",
        "fileOriginalName",
        "fileOriginalPath",
        "fileSizeBytes",
        "fileCreationDate",
        "fileModificationDate",
        "MD5",
        "SYSTEM",
        "SYSTEM_ID",
    ]
    columns = list(df.columns)
    for c in expected_columns:
        assert c in columns


def test_update_rosetta_paths_has_expected_original_paths(
    SC_transfer_2, report_for_transfer_2_one_id
):
    j = JsonInventory(report_for_transfer_2_one_id, root_dir=SC_transfer_2)
    df = j.update_rosetta_paths(j.df)
    paths = df["fileOriginalPath"].to_list()
    expected = [
        "\\multi_level_folder\\level_2\\یک نمونه فایل کامپیوتری.xlsx",
        "\\multi_level_folder\\level_2\\计算机文件示例.doc",
        "\\multi_level_folder\\קובץ מחשב לדוגמה.doc",
        "\\👪",
        "\\👪\\holiday2003.jpg",
        "\\👪\\😂😂😂.msg",
    ]
    for i in expected:
        assert i in paths


def test_update_rosetta_paths_has_expected_physical_paths(
    SC_transfer_2, report_for_transfer_2_one_id
):
    j = JsonInventory(report_for_transfer_2_one_id, root_dir=SC_transfer_2)
    df = j.update_rosetta_paths(j.df)
    paths = df["physical_path"].to_list()
    print(paths)
    for p in paths:
        assert os.path.exists(p)


def test_generate_inventory_retains_correct_original_path(json_inventory):
    json_data = json_inventory.build_rosetta_json().get("json")
    json_data.sort()
    expected = "\\😂😂😂.msg"
    result = json.loads(json_data[3])[0]
    result = result.get("fileOriginalPath")
    assert result == expected


def test_normalise_physical_path_capitalises_location(json_inventory):
    p = os.getcwd()
    expected = p[0].capitalize() + p[1:]
    result = json_inventory._normalise_physical_path(p)
    assert result == expected


def test_noramlise_physical_path_is_path_that_exists(json_inventory):
    p = os.getcwd()
    result = json_inventory._normalise_physical_path(p)
    assert os.path.exists(result)


@pytest.mark.parametrize("filename", [("test.txt"), ("😂😂😂.msg")])
def test_normalise_physical_path_works_for_files(json_inventory, tmp_path, filename):
    f = tmp_path / filename
    f.write_text("test", encoding="utf-8")
    result = json_inventory._normalise_physical_path(f)
    assert os.path.exists(result)


def test_build_rosetta_json_multiark_sip_has_record_for_each_file(
    report_for_transfer_1_multiple_arks, SC_transfer_1
):
    report = report_for_transfer_1_multiple_arks
    j = JsonInventory(report, root_dir=SC_transfer_1)
    json = j.build_rosetta_json().get("json")
    files = report["TYPE"].loc[lambda x: x == "File"].to_list()
    expected = len(files)
    result = len(json)
    assert result == expected


def test_build_rosetta_json_single_ark_sip_has_one_record(
    report_for_transfer_1_one_ark, SC_transfer_1
):
    report = report_for_transfer_1_one_ark
    j = JsonInventory(report, root_dir=SC_transfer_1)
    json = j.build_rosetta_json().get("json")
    expected = 1
    result = len(json)
    assert result == expected
