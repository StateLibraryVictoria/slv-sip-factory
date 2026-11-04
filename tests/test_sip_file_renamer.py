import os
import shutil
from lxml import etree as ET

import pytest

from rosetta_sip_factory import sip_builder as sb
from sip_file_renamer import *

# Setup test data.
input_path = os.path.join("tests", "test_data", "input")
sip_list = os.listdir(input_path)
output_path = os.path.join("tests", "test_data", "output")
output_renamed_path = os.path.join("tests", "test_data", "output_renamed")
percent_encoding_path = os.path.join("tests", "test_data", "percent_encoding")


@pytest.fixture
def percent_encoding_sip(tmp_path):
    test_data = os.path.join("tests", "test_data", "percent_encoding")
    output_dir = tmp_path / "percent_encoding"
    ie_dc_dict = {"dc:title": "percent encoded SIP"}
    sb.build_sip(
        ie_dmd_dict=ie_dc_dict,
        pres_master_dir=test_data,
        input_dir=test_data,
        generalIECharacteristics=[
            {"submissionReason": "bornDigitalContent", "IEEntityType": "periodicIE"}
        ],
        output_dir=output_dir,
    )
    return output_dir


### Refactor to use TMP instead of Output folder.
@pytest.fixture
def sip_with_hierarchy(tmp_path):
    folder_title = "test-SIP_A_sip_with_hierarchy_20240430"
    output_dir = tmp_path / folder_title
    title_parts = folder_title.split("_", 1)
    details = {
        "pi": title_parts[0],
        "title": title_parts[1:][0],
        "output": output_dir,
        "folder": folder_title,
    }
    return details


@pytest.fixture
def staged_sip_with_hierarchy(sip_with_hierarchy):
    cwd = os.getcwd()
    input_dir = os.path.join(
        cwd, "tests", "test_data", "input", sip_with_hierarchy.get("folder")
    )
    output_dir = sip_with_hierarchy.get("output")
    sb.build_sip(
        ie_dmd_dict=[
            {
                "dc:title": "test",  # title of IE, becomes dc:alternative once split.
            }
        ],
        pres_master_dir=input_dir,
        input_dir=input_dir,
        generalIECharacteristics=[
            {"submissionReason": "bornDigitalContent", "IEEntityType": "periodicIE"}
        ],
        sip_title="Heirarchy",
        output_dir=output_dir,
    )
    return output_dir


@pytest.fixture
def sip_with_unicode(tmp_path):
    folder_title = "test-SIP_An_example_sip_20240430"
    output_dir = tmp_path / folder_title
    title_parts = folder_title.split("_")
    details = {
        "folder": folder_title,
        "pi": title_parts[0],
        "title": "_".join(title_parts[1:]),
        "output": output_dir,
    }
    return details


@pytest.fixture
def staged_sip_with_unicode(sip_with_unicode):
    sip = sip_with_unicode
    cwd = os.getcwd()
    input_dir = os.path.join(cwd, "tests", "test_data", "input", sip.get("folder"))
    output_dir = sip.get("output")
    sb.build_sip(
        ie_dmd_dict=[
            {
                "dc:title": "test",  # title of IE, becomes dc:alternative once split.
            }
        ],
        pres_master_dir=input_dir,
        input_dir=input_dir,
        generalIECharacteristics=[
            {"submissionReason": "bornDigitalContent", "IEEntityType": "periodicIE"}
        ],
        sip_title="Heirarchy",
        output_dir=output_dir,
    )
    return output_dir


@pytest.fixture
def filenames():
    expected_names_1 = ["fid1-1.doc", "fid2-1.xlsx", "fid3-1.doc", "fid4-1.msg"]
    expected_names_2 = [
        "fid2-1.doc",
        "fid3-1.xlsx",
        "fid4-1.doc",
        "fid5-1.jpg",
        "fid6-1.msg",
    ]
    expected_names_1.sort()
    expected_names_2.sort()
    return {"unicode": expected_names_1, "hierarchy": expected_names_2}


def test_mets_for_unicode_sip(staged_sip_with_unicode):
    output_dir = staged_sip_with_unicode
    files = os.listdir(os.path.join(output_dir, "content"))
    files.sort()
    expected = ["mets.xml", "dc.xml", "streams"]
    expected.sort()
    print(files)
    assert files == expected


def test_mets_for_hierarchical_sip(staged_sip_with_hierarchy):
    output_dir = staged_sip_with_hierarchy
    files = os.listdir(os.path.join(output_dir, "content"))
    files.sort()
    expected = ["mets.xml", "dc.xml", "streams"]
    expected.sort()
    assert files == expected


# create a function that updates the filename href for output in output folder.


def test_move_renamed_unicode_files(staged_sip_with_unicode, filenames):
    # create the renamed data from the output folder data.
    output_dir = staged_sip_with_unicode

    # run function.
    move_rename_files(output_dir)

    # list files in renamed directory to check against expected
    renamed_files = os.listdir(
        os.path.join(output_dir, "content", "streams", "renamed")
    )
    renamed_files.sort()
    expected = filenames.get("unicode")
    assert expected == renamed_files


def test_move_renamed_heirarchy_files(staged_sip_with_hierarchy, filenames):
    # create the renamed data from the output folder data.
    output_dir = staged_sip_with_hierarchy

    # run function.
    move_rename_files(output_dir)

    # list files in renamed directory to check against expected
    renamed_files = os.listdir(
        os.path.join(output_dir, "content", "streams", "renamed")
    )
    renamed_files.sort()
    expected = filenames.get("hierarchy")
    assert expected == renamed_files


def test_updated_manifest_for_renamed_files_hierarchy(
    staged_sip_with_hierarchy, filenames
):
    output_dir = staged_sip_with_hierarchy
    move_rename_files(output_dir)
    expected = filenames.get("hierarchy")
    mets_file = os.path.join(output_dir, "content", "mets.xml")
    mets = ET.parse(mets_file)
    updated_list = []
    for fl in mets.findall(".//{http://www.loc.gov/METS/}FLocat"):
        fl_id = fl.getparent().attrib["ID"]
        path, name = os.path.split(fl.attrib["{http://www.w3.org/1999/xlink}href"])
        print(path)
        print(name)
        if "renamed" in path:
            print("renamed in path")
            updated_list.append(name)
    assert updated_list == expected


# Test no files have gone missing.
def test_all_files_are_in_both_locations(staged_sip_with_hierarchy):
    cwd = os.getcwd()
    output_dir = staged_sip_with_hierarchy
    input_dir = os.path.join(cwd, "tests", "test_data", "input", output_dir.parts[-1])
    output_dir = os.path.join(output_dir, "content", "streams")
    for root, dirs, files in os.walk(input_dir):
        numInput = len(files)
    for root, dirs, files in os.walk(output_dir):
        numOutput = len(files)
    assert numInput == numOutput


def test_percent_encoding_for_ascii_filenames(percent_encoding_sip):
    output_dir = percent_encoding_sip

    move_rename_files(output_dir)
    mets_file = os.path.join(output_dir, "content", "mets.xml")
    mets = ET.parse(mets_file)
    expected = [
        "New%20Text%20Document.txt",
        "something%25sign/This%20That.txt",
        "something%25sign/This%2520That.txt",
    ]
    output = []
    for fl in mets.findall(".//{http://www.loc.gov/METS/}FLocat"):
        output.append(fl.attrib["{http://www.w3.org/1999/xlink}href"])
    print(output)
    assert expected == output


# Test dc.xml has been created
def test_dc_xml_in_output(staged_sip_with_hierarchy):
    dcxml = os.path.join(staged_sip_with_hierarchy, "content", "dc.xml")
    assert os.path.isfile(dcxml) == True


# Test rosetta:externalId in dc.xml
@pytest.mark.parametrize(
    "input_folder, expected",
    [
        (
            sip_list[0],
            '<dc:record xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:rosetta="http://www.exlibrisgroup.com/dps"><rosetta:externalId>test-add-pi-to-xml</rosetta:externalId><rosetta:externalSystem>test_system</rosetta:externalSystem><dc:title>test_sip_metadata_test-SIP_An_example_sip_20240430</dc:title></dc:record>',
        ),
        (
            sip_list[1],
            '<dc:record xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:rosetta="http://www.exlibrisgroup.com/dps"><rosetta:externalId>test-add-pi-to-xml</rosetta:externalId><rosetta:externalSystem>test_system</rosetta:externalSystem><dc:title>test_sip_metadata_test-SIP_A_sip_with_hierarchy_20240430</dc:title></dc:record>',
        ),
    ],
)
def test_generate_dcxml(input_folder, expected):
    logging.error(input_folder)
    record = generate_dcxml_record(
        "test-add-pi-to-xml",
        "test_system",
        "test_sip_metadata_" + input_folder,
    )
    record = ET.tostring(record).decode()
    logging.error(record)
    logging.error(expected)
    print(record)
    print(expected)
    assert record == expected
