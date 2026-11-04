from abc import ABC, abstractmethod
import logging


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

    def __init__(
        self,
        uuid,
        df,
        bagit_agent="bagit.py <https://github.com/LibraryOfCongress/bagit-python>",
    ):
        self.uuid = uuid
        self.df = df
        self.bagit_agent = bagit_agent

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
                    "eventOutcomeDetail1": f"Files: {files[i]}, bytes: {bytes[i]}, transferred by: {contact[i]}, with collection id: {collection_id[i]}. Resulted in folder: {outcome_folder[i]}. Transfer completed using: {self.bagit_agent}",
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
                    "eventDescription": f"Bag integrity validated at path '{bag_path[i]}' by {self.bagit_agent}",
                    "eventDateTime": end_time[i],
                    "eventOutcome1": outcome[i],
                    "eventOutcomeDetail1": errors[i],
                }
            )
        return events
