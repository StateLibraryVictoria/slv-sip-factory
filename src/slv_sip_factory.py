from abc import ABC, abstractmethod
import os
from lxml import etree as ET
import urllib.parse
import shutil
import logging
from pathlib import PurePath
import json
from rosetta_sip_factory import sip_builder
from src.sip_json_factory import JsonInventory
import errno

bagit_agent = "bagit.py <https://github.com/LibraryOfCongress/bagit-python>"


def _move_files_from_json_fix(json_doc, streams_dir):
    if type(json_doc) == str:
        rep_dict = json.loads(json_doc)
    else:
        rep_dict = json_doc
    for item in rep_dict:
        origin = item["physical_path"]
        destination = item["fileOriginalPath"]
        destination_dir = os.path.dirname(destination)
        logging.error(destination_dir)
        if destination_dir == "\\":
            outpath = streams_dir
            logging.error("matches")
        else:
            outpath = os.path.join(streams_dir, destination_dir)
            logging.error("doesn't match")
        logging.error(outpath)
        if not os.path.exists(outpath):
            try:
                os.makedirs(outpath)
            except OSError as exc:  # Guard against race condition
                if exc.errno is not errno.EEXIST:
                    raise
        shutil.copy2(origin, outpath)


sip_builder._move_files_from_json = _move_files_from_json_fix


class EventCreator(ABC):

    @abstractmethod
    def factory_method(self, uuid, df):
        pass

    def build_events(self, type, uuid, df) -> str:
        creator = self.factory_method(type, uuid, df)
        events = creator.parse_events()

        return events


class ConcreteEventCreator(EventCreator):
    def factory_method(self, type, uuid, df) -> DepositEvent:
        if type == "validation":
            return ValidationEvent(uuid, df)
        elif type == "transfer":
            return TransferEvent(uuid, df)
        else:
            logging.error(f"Event type not implemented: {type}")


class DepositEvent(ABC):
    """Designed to be submitted to the eventList aspect of the Rosetta_Sip_Factory.
    A list of dictionaries. Allowed keys are
        'eventIdentifierType', 'eventIdentifierValue', 'eventType',
        'eventDescription', 'eventDateTime', 'eventOutcome1',
        'eventOutcomeDetail1', 'eventOutcomeDetailExtension1',
        'eventOutcome2', 'eventOutcomeDetail2',
        'eventOutcomeDetailExtension2', 'eventOutcome2',
        'eventOutcomeDetail2', 'eventOutcomeDetailExtension2',
        'linkingAgentIdentifierXMLID1',
        'linkingAgentIdentifierType1',
        'linkingAgentIdentifierValue1', 'linkingAgentRole1',
        'linkingAgentIdentifierXMLID2',
        'linkingAgentIdentifierType2',
        'linkingAgentIdentifierValue2', 'linkingAgentRole2',
        'linkingAgentIdentifierXMLID3',
        'linkingAgentIdentifierType3',
        'linkingAgentIdentifierValue3' and 'linkingAgentRole3'.
        Values must be strings. e.g.
        [{'eventType': 'PRE-DEPOSIT',
          'eventDescription': 'changed foo to bar',
          'eventDateTime': '2016-03-14 14:22:01',
          'eventOutcome1': 'SUCCESS'}]
        The list may contain any number of dictionaries. Each
        dictionary represents a separate event."""

    def __init__(self, uuid, df):
        self.uuid = uuid
        self.df = df

    @abstractmethod
    def parse_events(self) -> list[dict]:
        pass

    def normalise_events(self) -> None:
        df = self.df
        col_names = df.columns
        if "Outcome" in col_names:
            df["Outcome"] = df["Outcome"].replace("Pass", "Success")
            df["Outcome"] = df["Outcome"].replace("Fail", "Failure")
        if "Errors" in col_names:
            df["Errors"] = df["Errors"].replace("", "No errors.")
            df["Errors"] = df["Errors"].fillna("No errors.")
        for id in ["TransferID", "OutcomeIdentifier", "PayloadOxum"]:
            if id in col_names:
                df[id] = df[id].astype(str)


class CarrierImagingEvent(DepositEvent):

    def parse_events(self):
        logging.error("Carrier imaging event not implemented")
        pass


class TransferEvent(DepositEvent):

    def parse_events(self):
        self.normalise_events()
        event_df = self.df.loc[self.df["BagUUID"] == self.uuid]
        action_ids = event_df["TransferID"].to_list()
        dates = event_df["EndTime"].to_list()
        outcome_folder = event_df["OutcomeFolderTitle"].to_list()
        collection_id = event_df["CollectionIdentifier"].to_list()
        contact = event_df["ContactName"].to_list()
        payload_oxum = event_df["PayloadOxum"].to_list()
        files = [x.split(".")[1] for x in payload_oxum]
        bytes = [x.split(".")[0] for x in payload_oxum]
        event_type = "PRE-DEPOSIT"
        events = []
        for i in range(len(action_ids)):
            events.append(
                {
                    "eventType": event_type,
                    "eventIdentifierType": "bagitWorkflowTransferOutcomeId",
                    "eventIdentifierValue": action_ids[i],
                    "eventDescription": f"Transferred to statecollectionstore.",
                    "eventDateTime": dates[i],
                    "eventOutcome1": "Success",
                    "eventOutcomeDetail1": f"Files: {files[i]}, bytes: {bytes[i]}, transferred by: {contact[i]}, with collection id: {collection_id[i]}. Resulted in folder: {outcome_folder[i]}. Transfer completed using: {bagit_agent}",
                }
            )
        events.append(
            {
                "eventType": event_type,
                "eventIdentifierType": "bagitWorkflowAssignBagUUID",
                "eventIdentifierValue": f"bagitWorkflow-{self.uuid}",
                "eventDescription": f"Assigned UUID to transfer.",
                "eventDateTime": dates[0],
                "eventOutcome1": "Success",
            }
        )
        return events


class ValidationEvent(DepositEvent):

    def parse_events(self):
        self.normalise_events()
        event_df = self.df.loc[self.df["BagUUID"] == self.uuid]
        action_ids = event_df["OutcomeIdentifier"].to_list()
        outcome = event_df["Outcome"].to_list()
        errors = event_df["Errors"].to_list()
        bag_path = event_df["BagPath"].to_list()
        start_time = event_df["StartTime"].to_list()
        end_time = event_df["EndTime"].to_list()
        event_type = "PRE-DEPOSIT"
        events = []
        for i in range(len(action_ids)):
            events.append(
                {
                    "eventType": event_type,
                    "eventIdentifierType": "bagitWorkflowValidationOutcomeId",
                    "eventIdentifierValue": action_ids[i],
                    "eventDescription": f"Bag integrity validated at path '{bag_path[i]}' by {bagit_agent}",
                    "eventDateTime": end_time[i],
                    "eventOutcome1": outcome[i],
                    "eventOutcomeDetail1": errors[i],
                }
            )
        return events


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

    def build_sip_from_json(
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
