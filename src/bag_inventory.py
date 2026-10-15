import pandas as pd
import os
import platform
from urllib.parse import unquote, urlparse
from time import strftime
from pathlib import Path
import logging


class BagInventory:
    def __init__(
        self,
        df: pd.DataFrame,
        root_dir: str = "",
        allowed_systems: list = ["alma", "archivesspace"],
        unquote: bool = False,
    ):
        """
        Builds an inventory of description and decisions which can be output as JSON.

        Keyworkd arguments:
        df -- Pandas DataFrame containing DROID report with added columns for description and decisions.
        root_dir -- the root directory desired for the output filepaths. (default "")
        allowed_systems -- list of systems where identifiers may be valid. Used for validation. (default ["alma", "archivesspace"])
        unquote -- set to True to process unicode characters rather than html encoded. (default False)
        """
        self.df = df
        self.root_dir = os.path.normpath(root_dir)
        self.allowed_systems = allowed_systems
        self.unquote = unquote
        self.has_archive_files = False
        self._drop_archive_contents()
        self._update_paths()
        self._normalise_system_fields()
        self.prefix = None

    def _update_paths(self):
        columns = len(self.df.columns)
        self.df["PATH"] = self.df.URI.apply(lambda x: urlparse(x).path)
        self.df.PATH = self.df.PATH.apply(self._tidy_path)
        if unquote:
            self.df.PATH = self.df.PATH.apply(unquote)
        self.prefix = self.df.PATH[0]
        self.df.PATH = self.df.PATH.str.replace(self.prefix, self.root_dir, regex=False)

    def _tidy_path(self, path):
        path = os.path.normpath(path)
        path = str(Path(path).resolve())
        return path

    def _drop_archive_contents(self, pattern=("iso", "zip", "tar", "gzip")):
        size = self.df.size
        self.df = self.df[~self.df.URI.str.startswith(pattern)]
        dropped_size = self.df.size
        self.has_archive_files = size > dropped_size

    def _normalise_system_fields(self):
        if "SYSTEM_ID" in self.df.columns:
            self.df.SYSTEM_ID = self.df.SYSTEM_ID.fillna("")
        if "SYSTEM" in self.df.columns:
            self.df.SYSTEM = self.df.SYSTEM.fillna("")

    def get_inventory_metadata(self, creator: str, process: str) -> dict:
        types = self.df.TYPE.value_counts().to_dict()
        return {
            "time": strftime("%Y-%m-%d:%H%M%S"),
            "created_by": creator,
            "process": process,
            "platform": platform.platform(),
            "script": __file__,
            "python_version": platform.python_version(),
            "file_count": types.get("File", 0) + types.get("Container", 0),
            "folder_count": types.get("Folder", 0),
            "has_archive_files": self.has_archive_files,
        }

    def _get_decision_dict(self, df, reason=None):
        data = {}
        if reason is not None:
            df = df[df["REASON"] == reason]
            data.update({"reason-text": reason})
        files = df["PATH"].to_list()
        files.sort()
        data.update({"files": files})
        return data

    def _get_reasons_list(self, df) -> list:
        reasons = list(set(df["REASON"].to_list()))
        reason_dicts = [self._get_decision_dict(df, x) for x in reasons]
        return reason_dicts

    def _get_filelists_by_identifier(self, df) -> dict:
        identifier_dict = {}
        unique_ids = list(set(df.SYSTEM_ID.to_list()))
        for id in unique_ids:
            just_id = df[df.SYSTEM_ID == id]
            files = just_id.PATH.to_list()
            files.sort()
            identifier_dict.update({id: files})
        return identifier_dict

    def get_decision_inventory(self):
        df = self.df
        data = {"retain-state-collection": {}, "retain-record": {}, "dispose": {}}
        state_collection_df = df[df["DECISION"] == "retain-state-collection"]
        record_df = df[df["DECISION"] == "retain-record"]
        dispose_df = df[df["DECISION"] == "dispose"]
        check_df = df[df["DECISION"] == "check"]

        data.update(
            {"retain-state-collection": [self._get_decision_dict(state_collection_df)]}
        )
        data.update({"retain-record": self._get_reasons_list(record_df)})
        data.update({"dispose": self._get_reasons_list(dispose_df)})
        if not check_df.empty:
            data.update({"check": self._get_reasons_list(check_df)})
        return data

    def get_description_inventory(self):
        if "SYSTEM" not in self.df.columns or "SYSTEM_ID" not in self.df.columns:
            logging.info("SYSTEM or SYSTEM_ID not in data.")
            return None
        df = self.df[self.df["SYSTEM"].notna()]
        df = df.reset_index()
        df.SYSTEM = df.SYSTEM.str.lower()
        data = {}
        for system in self.allowed_systems:
            test_df = df[df["SYSTEM"] == system.lower()]
            if not test_df.empty:
                record_dict = self._get_filelists_by_identifier(test_df)
                data.update({system: record_dict})
        return data

    def _validate_reasons(self):
        # if a decision is not retain-state-collection it must have a reason
        unreasoned_decisions = self.df.query(
            "((DECISION != 'retain-state-collection') & (DECISION != '')) & (REASON == '')"
        )
        if not unreasoned_decisions.empty:
            logging.warning(f"Reasons not recorded for required retention decisions.")
            logging.warning(unreasoned_decisions["DECISION"].to_list())
            logging.warning(unreasoned_decisions["REASON"].to_list())
            return False
        return True

    def _validate_description(self):
        # only retain-state-collection material can have description
        inconsistent_decision = self.df.query(
            "(SYSTEM_ID != '') & (DECISION != 'retain-state-collection')"
        )
        if not inconsistent_decision.empty:
            logging.warning(
                f"Description applied to files not marked retain-state-collection"
            )
            paths = inconsistent_decision.PATH.apply(unquote)
            logging.info(inconsistent_decision.SYSTEM_ID)
            logging.warning(f"Files: {';, '.join(paths.to_list())}")
        # if description exists it must have both system and system_id
        description_mismatch = self.df.query(
            "((SYSTEM == '') & (SYSTEM_ID != '')) | ((SYSTEM_ID == '') & (SYSTEM != ''))"
        )
        if not description_mismatch.empty:
            logging.warning(f"Some expected fields are empty in SYSTEM and SYSTEM_ID.")
            paths = description_mismatch.PATH.apply(unquote)
            logging.warning(f"Files: {';, '.join(paths.to_list())}")

        return inconsistent_decision.empty and description_mismatch.empty

    def _validate_all_files_have_decisions(self):
        files_without_decisions = self.df.query("(TYPE == 'File') & (DECISION == '')")
        if not files_without_decisions.empty:
            logging.warning("Not all files have decisions.")
            logging.warning(
                f"Missing decisions for files: {", ".join(files_without_decisions["URI"].to_list())}"
            )
            return False
        return True

    def validate(self, description=True):
        decisions_have_reasons = self._validate_reasons()
        description_is_valid = self._validate_description()
        if not description:
            description_is_valid = True
        files_have_decisions = self._validate_all_files_have_decisions()

        return decisions_have_reasons and description_is_valid and files_have_decisions
