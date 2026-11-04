import os
from lxml import etree as ET
import urllib.parse
import shutil
import logging
from pathlib import PurePath
import json
from rosetta_sip_factory import sip_builder
from src.sip_json_factory import JsonInventory
from src.event_handlers import ConcreteEventCreator
import errno


def _move_files_from_json_fix(json_doc, streams_dir):
    """Bug in sip_builder._move_files_from_json means that files at the
    root of the SIP are lost due to behaviour of os.path.join when the final
    path part is '\\'"""
    if type(json_doc) == str:
        rep_dict = json.loads(json_doc)
    else:
        rep_dict = json_doc
    for item in rep_dict:
        origin = item["physical_path"]
        destination = item["fileOriginalPath"]
        # this is a horrible hack
        destination_dir = destination.split("\\")
        destination_dir = "\\".join(destination_dir[1:-1])
        if destination_dir == "\\":
            outpath = streams_dir
        else:
            destination_dir = os.path.normpath(destination_dir)
            outpath = os.path.join(streams_dir, destination_dir)
        if not os.path.exists(outpath):
            try:
                os.makedirs(outpath)
            except OSError as exc:  # Guard against race condition
                if exc.errno is not errno.EEXIST:
                    raise
        shutil.copy2(origin, outpath)


sip_builder._move_files_from_json = _move_files_from_json_fix


class SlvSipFactory:
    def __init__(self, validation_df=None, transfer_df=None):
        self.validation_df = validation_df
        self.transfer_df = transfer_df

    ## to do:
    # renaming
    # using existing factory functions
    def build_sip(
        self,
        bag_uuid,
        input_dir,
        output_dir,
        pres_master_dir,
        sip_title,
    ):
        events = self.compile_events(bag_uuid)
        identifier = [
            {
                "objectIdentifierType": "transferBagUUID",
                "objectIdentifierValue": bag_uuid,
            }
        ]
        sip_builder.build_sip(
            ie_dmd_dict=[{"dc:title": sip_title}],
            eventList=events,
            input_dir=input_dir,
            output_dir=output_dir,
            pres_master_dir=pres_master_dir,
            objectIdentifier=identifier,
            sip_title=sip_title,
        )

    def build_sip_from_manifest(
        self,
        bag_uuid,
        input_dir,
        output_dir,
        sip_title,
        transfer_manifest,
    ):
        j = JsonInventory(transfer_manifest, input_dir)
        events = self.compile_events(bag_uuid)

        json_dict = j.build_rosetta_json()
        json_list = json_dict.get("json")
        id_list = json_dict.get("record_ids")
        bag_info = j.load_bag_info()
        description = bag_info.get("External-Description")[0]
        date_submitted = bag_info.get("Bagging-Date")[0]
        is_part_of = bag_info.get("Internal-Sender-Identifier")[0]
        base_dc = {
            "dc:description": description,
            "dc:dateSubmitted": date_submitted,
            "dc:isPartOf": is_part_of,
        }
        for i in range(len(json_list)):
            identifier = [
                {
                    "objectIdentifierType": "record_id",
                    "objectIdentifierValue": id_list[i],
                }
            ]
            transfer_dir = os.path.join(output_dir, f"transfer_{i+1}")
            os.mkdir(transfer_dir)
            dc = base_dc.copy()
            dc.update({"dc:identifier": id_list[i]})
            record_data = json_list[i]
            sip_builder.build_sip_from_json(
                ie_dmd_dict=[dc],
                pres_master_json=record_data,
                eventList=events,
                objectIdentifier=identifier,
                output_dir=transfer_dir,
                sip_title=sip_title,
            )

    def compile_events(self, bag_uuid):
        creator = ConcreteEventCreator()
        events = []
        if self.validation_df is not None:
            validation_events = creator.build_events(
                "validation", bag_uuid, self.validation_df
            )
            events.extend(validation_events)

        if self.transfer_df is not None:
            transfer_events = creator.build_events(
                "transfer", bag_uuid, self.transfer_df
            )
            events.extend(transfer_events)
        logging.debug(events)
        return events

    def move_rename_files(root_directory, mets_filename="mets.xml"):
        """A function that takes an existing SIP, checks for non-ascii filenames, creates a renamed
        copy of those files in a renamed/ directory in streams and updates the href tag in the FLocat
        area of the METS manifest.

        Args:
            root_directory (path/str) : The location of the SIP.
            mets_filename (str) : Defaults to "mets.xml", but can be used to specify filename if one has been used.
        """
        # Parse the mets from the file location.
        mets_file = os.path.join(root_directory, "content", mets_filename)
        mets = ET.parse(mets_file)

        # Set the directory for renamed files.
        rename_dir = os.path.join(root_directory, "content", "streams", "renamed")
        if os.path.exists(rename_dir):
            rename_dir = os.path.join(rename_dir, "slv_rosetta_sip_preparation")

        # Iterate through files and rename them if they are not ASCII.
        ## Update the href so that the file can be resolved.
        for fl in mets.findall(".//{http://www.loc.gov/METS/}FLocat"):
            fl_id = fl.getparent().attrib["ID"]
            root, ext = os.path.splitext(
                fl.attrib["{http://www.w3.org/1999/xlink}href"]
            )
            if not root.isascii():
                logging.info(
                    f"File: {root + ext} with file id {fl_id} contains non-ascii characters. File will be renamed."
                )
                fl.attrib["{http://www.w3.org/1999/xlink}href"] = PurePath(
                    os.path.join("renamed", fl_id + ext)
                ).as_posix()
                logging.debug(f"METS updated for file {root+ext}")
                if not os.path.exists(rename_dir):
                    os.mkdir(rename_dir)
                logging.info("Copying file to new location...")
                try:
                    shutil.copy2(
                        os.path.join(root_directory, "content", "streams", root + ext),
                        os.path.join(rename_dir, fl_id + ext),
                    )
                    logging.info("File copied.")
                except Exception as e:
                    print(f"Error copying file: {root+ext}. Error message: {e}")
                    logging.error(f"Error copying file: {root+ext}. Error message: {e}")
            else:  # Percent encodes all other refs.
                fl.attrib["{http://www.w3.org/1999/xlink}href"] = urllib.parse.quote(
                    fl.attrib["{http://www.w3.org/1999/xlink}href"], encoding="utf-8"
                )
        with open(mets_file, "wb") as mf:
            mf.write(ET.tostring(mets, xml_declaration=True, encoding="utf-8"))
        return None
