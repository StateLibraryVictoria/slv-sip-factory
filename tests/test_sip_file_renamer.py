import os
import shutil
from lxml import etree as ET

import pytest

from rosetta_sip_factory import sip_builder as sb
from src.sip_file_renamer import *

# Setup test data.
input_path = os.path.join("tests", "test_data", "input")
sip_list = os.listdir(input_path)
output_path = os.path.join("tests", "test_data", "output")
output_renamed_path = os.path.join("tests", "test_data", "output_renamed")
percent_encoding_path = os.path.join("tests", "test_data", "percent_encoding")


# test based on rosetta_sip_factory_test
@pytest.mark.parametrize("input_folder", [sip_list[0], sip_list[1]])
def test_mets_dnx(input_folder):
    """Test basic construction of METS DNX"""
    input_dir = os.path.join(input_path, input_folder)
    output_dir = os.path.join(output_path, input_folder)
    parts = input_folder.split("_")
    pi = parts[0]
    title = " ".join(parts[1:])

    # first off, delete anything that's in the output folder
    shutil.rmtree(output_dir)
    os.makedirs(output_dir)
    sb.build_sip(
        ie_dmd_dict=[
            {
                "dc:title": title,  # title of IE, becomes dc:alternative once split.
                "rosetta:externalId": pi,
                "rosetta:externalSystem": "ArchivesSpace",
            }
        ],
        pres_master_dir=input_dir,
        input_dir=input_dir,
        generalIECharacteristics=[
            {"submissionReason": "bornDigitalContent", "IEEntityType": "periodicIE"}
        ],
        sip_title=title,
        output_dir=output_dir,
    )
    files = os.listdir(os.path.join(output_dir, "content"))
    files.sort()
    expected = ["mets.xml", "dc.xml", "streams"]
    expected.sort()
    print(files)
    assert files == expected


# create a function that updates the filename href for output in output folder.
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


@pytest.mark.parametrize(
    "input_folder, expected",
    [(sip_list[0], expected_names_1), (sip_list[1], expected_names_2)],
)
def test_move_renamed_files(input_folder, expected):
    # create the renamed data from the output folder data.
    output_dir = os.path.join(output_path, input_folder)
    renamed_output = os.path.join(output_renamed_path, input_folder)
    # cleanup old output if it exists:
    if os.path.exists(renamed_output):
        shutil.rmtree(renamed_output)

    # copy files to directory.
    shutil.copytree(output_dir, renamed_output)

    # load mets from file.
    mets_file = os.path.join(renamed_output, "content", "mets.xml")
    mets = ET.parse(mets_file)

    # run function.
    move_rename_files(renamed_output)

    # list files in renamed directory to check against expected
    renamed_files = os.listdir(
        os.path.join(renamed_output, "content", "streams", "renamed")
    )
    renamed_files.sort()

    assert expected == renamed_files

    # Checks the updated manifest.


@pytest.mark.parametrize(
    "input_folder, expected",
    [(sip_list[0], expected_names_1), (sip_list[1], expected_names_2)],
)
def test_updated_manifest_for_renamed_files(input_folder, expected):
    renamed_output = os.path.join(output_renamed_path, input_folder)
    mets_file = os.path.join(renamed_output, "content", "mets.xml")
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
@pytest.mark.parametrize("input_folder", [sip_list[0], sip_list[1]])
def test_all_files_are_in_both_locations(input_folder):
    input_dir = os.path.join(output_path, input_folder)
    renamed_output = os.path.join(output_renamed_path, input_folder)
    for root, dirs, files in os.walk(input_dir):
        numInput = len(files)
    for root, dirs, files in os.walk(renamed_output):
        numOutput = len(files)
    assert numInput == numOutput


def test_percent_encoding_for_ascii_filenames():
    input_dir = percent_encoding_path
    output_dir = os.path.join("tests", "test_data", "percent_output")
    title = "Test percent encoding"

    # first off, delete anything that's in the output folder
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
        os.makedirs(output_dir)
    ie_dc_dict = {"dc:title": title}
    sb.build_sip(
        ie_dmd_dict=ie_dc_dict,
        pres_master_dir=input_dir,
        input_dir=input_dir,
        generalIECharacteristics=[
            {"submissionReason": "bornDigitalContent", "IEEntityType": "periodicIE"}
        ],
        output_dir=output_dir,
    )
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
@pytest.mark.parametrize("input_folder", [sip_list[0], sip_list[1]])
def test_dc_xml_in_output(input_folder):
    dcxml = os.path.join(output_renamed_path, input_folder, "content", "dc.xml")
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
    record = generate_dcxml_record(
        "test-add-pi-to-xml",
        "test_system",
        "test_sip_metadata_" + input_folder,
    )
    record = ET.tostring(record).decode()
    print(record)
    print(expected)
    assert record == expected
