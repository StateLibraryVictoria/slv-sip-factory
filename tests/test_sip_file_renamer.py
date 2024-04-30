import os
import shutil
from lxml import etree as ET

import pytest

from rosetta_sip_factory import sip_builder as sb
from sip_file_renamer import *

# Setup test data.
input_path = os.path.join("tests","test_data","input")
sip_list = os.listdir(input_path)
print(sip_list)
output_path = os.path.join("tests","test_data","output")
output_renamed_path = os.path.join("tests","test_data","output_renamed")
"""validation_schema_file = os.path.join("tests", "test_data", "mets_schema.xsd")
with open(validation_schema_file, 'r', encoding='utf-8') as file:
     xml_schema_doc = ET.parse(file)
     xmlschema = ET.XMLSchema(xml_schema_doc)
"""
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
    ie_dc_dict = {"dc:title": title}
    sb.build_sip(
        ie_dmd_dict=ie_dc_dict,
        pres_master_dir=input_dir,
        input_dir=input_dir,
        generalIECharacteristics=[
                {'submissionReason': 'bornDigitalContent',
                 'IEEntityType': 'periodicIE'}
                ],
        output_dir=output_dir
        )

# create a function that updates the filename href for output in output folder.
expected_names_1 = ['fid1-1.doc', 'fid2-1.xlsx', 'fid3-1.doc', 'fid4-1.msg']
expected_names_2 = ['fid2-1.doc', 'fid3-1.xlsx', 'fid4-1.doc','fid5-1.jpg','fid6-1.msg']
expected_names_1.sort()
expected_names_2.sort()


@pytest.mark.parametrize("input_folder, expected", [(sip_list[0], expected_names_1), (sip_list[1], expected_names_2)])
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
    renamed_files = os.listdir(os.path.join(renamed_output,'content','streams','renamed'))
    renamed_files.sort()
    
    assert(expected == renamed_files)

    # Checks the updated manifest.
@pytest.mark.parametrize("input_folder, expected", [(sip_list[0], expected_names_1), (sip_list[1], expected_names_2)])
def test_updated_manifest_for_renamed_files(input_folder, expected):    
    renamed_output = os.path.join(output_renamed_path, input_folder)
    mets_file = os.path.join(renamed_output, "content", "mets.xml")
    mets = ET.parse(mets_file)
    updated_list = []
    for fl in mets.findall(".//{http://www.loc.gov/METS/}FLocat"):
            fl_id = fl.getparent().attrib['ID']
            path, name = os.path.split(fl.attrib["{http://www.w3.org/1999/xlink}href"])
            print(path)
            print(name)
            if "renamed" in path:
                 print("renamed in path")
                 updated_list.append(name)
    assert(updated_list == expected)


# Test no files have gone missing.
@pytest.mark.parametrize("input_folder", [sip_list[0], sip_list[1]])
def test_all_files_are_in_both_locations(input_folder):
    input_dir = os.path.join(output_path, input_folder)
    renamed_output = os.path.join(output_renamed_path, input_folder)
    for root, dirs, files in os.walk(input_dir):
        numInput = len(files)
    for root, dirs, files in os.walk(renamed_output):
        numOutput = len(files)
    assert(numInput == numOutput)