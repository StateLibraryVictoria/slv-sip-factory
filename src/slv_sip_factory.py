from abc import ABC, abstractmethod
import os
from lxml import etree as ET
import urllib.parse
import shutil
import logging
from pathlib import PurePath


class EventCreator(ABC):

    @abstractmethod
    def factory_method(self, uuid, df):
        pass

    def build_events(self, uuid, df) -> str:
        events = self.factory_method(uuid, df)

        result = f"Creator parsed new event."
        return events


class ConcreteCarrierImagingEventCreator(EventCreator):
    def factory_method(self, uuid, df) -> DepositEvent:
        return CarrierImagingEvent(uuid, df)


class ConcreteValidationEventCreator(EventCreator):
    def factory_method(self, uuid, df) -> DepositEvent:
        return ValidationEvent(uuid, df)


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

    @abstractmethod
    def parse_events(self) -> list[dict]:
        pass


class CarrierImagingEvent(DepositEvent):
    def __init__(self, uuid, df):
        self.uuid = uuid
        self.df = df

    def parse_events(self):
        logging.error("Carrier imaging event not implemented")
        pass


class TransferEvent(DepositEvent):
    def __init__(self, uuid, df):
        self.uuid = uuid
        self.df = df

    def parse_events(self):
        logging.error("Transfer events not implemented")
        pass


class ValidationEvent(DepositEvent):
    def __init__(self, uuid, df):
        self.uuid = uuid
        self.df = df

    def parse_events(self):
        event_df = self.df.loc[self.df["BagUUID"] == self.uuid]
        event_df["Errors"] = event_df["Errors"].replace("", "No errors.")
        event_df["OutcomeIdentifier"] = event_df["OutcomeIdentifier"].astype(str)
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
                    "eventDescription": f"Bag integrity validated at path '{bag_path[i]}'",
                    "eventDateTime": end_time[i],
                    "eventOutcome1": outcome[i],
                    "eventOutcomeDetail1": errors[i],
                }
            )
        return events


class SlvSipFactory:
    pass

    ## to do:
    # renaming
    # using existing factory functions

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
