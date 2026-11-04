import logging
import pandas as pd
from src.bag_inventory import BagInventory
from urllib.parse import unquote
from datetime import datetime
import os


class JsonInventory(BagInventory):
    def __init__(
        self,
        df: pd.DataFrame,
        root_dir="",
        allowed_systems=["alma", "archivesspace"],
        unquote=False,
        is_bag=True,
    ):
        self.manifest_dir = None
        if is_bag == True and not os.path.basename(root_dir) == "data":
            self.manifest_dir = root_dir
            root_dir = os.path.join(root_dir, "data")
        super().__init__(
            df,
            root_dir,
            allowed_systems,
            unquote,
        )
        self.is_bag = is_bag
        self.checksums = self.load_file_checksums()

    def build_rosetta_json(self) -> dict:
        """Returns lists of json and system information.

        Returns dict with keys 'json' and 'record_ids' containing lists of respective values
        """
        # one record per IE
        json_list = []
        if not "SYSTEM" in self.df.columns and not "SYSTEM_ID" in self.df.columns:
            raise (ValueError("System metadata not present."))
        state_coll_df = self.df[self.df["DECISION"] == "retain-state-collection"]
        # drop things that aren't files as Rosetta can't handle them.
        state_coll_df = state_coll_df[state_coll_df["TYPE"] == "File"]
        logging.info(f"Processing {state_coll_df.count} records")
        unique_ids = list(set(state_coll_df["SYSTEM_ID"].to_list()))
        logging.info(f"Processing {len(unique_ids)} records into individual IEs")
        for id in unique_ids:
            working_df = state_coll_df[state_coll_df["SYSTEM_ID"] == id]
            data = self.build_representation(working_df)
            json_list.append(data)
        rosetta_data = {"json": json_list, "record_ids": unique_ids}
        return rosetta_data

    def build_representation(self, df: pd.DataFrame) -> str:
        """
        from rosetta_sip_factory_requirements:
        - *physical_path (the actual location of the file on the filesystem)
        - *fileOriginalName
        - *fileOriginalPath (the filepath as it should display in the METS)
        - MD5 (not mandatory, but highly recommended)
        - fileSizeBytes
        - fileCreationDate
        - fileModificationDate
        - label
        - note
        """
        df = self.update_rosetta_paths(df)
        df = self.get_file_information(df)
        # drop unneeded columns
        required = [
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
        to_drop = []
        for c in df.columns:
            if c not in required:
                to_drop.append(c)
        df = df.drop(columns=to_drop)
        # convert to JSON

        output = df.to_json(orient="records", force_ascii=False)
        return output

    def update_rosetta_paths(self, df: pd.DataFrame):
        df["PATH"] = df["PATH"].apply(unquote)
        df["PATH"] = df["PATH"].apply(os.path.normpath)
        df["physical_path"] = df["PATH"].apply(self._tidy_path)
        df["fileOriginalName"] = df["PATH"].apply(self._normalise_file_original_name)
        df["fileOriginalPath"] = df["PATH"].str.replace(self.root_dir, "")
        return df

    def get_file_information(self, df: pd.DataFrame):
        df["stat"] = df["physical_path"].apply(os.stat)
        df["fileCreationDate"] = df["stat"].apply(lambda x: x.st_birthtime)
        df["fileCreationDate"] = df["fileCreationDate"].apply(
            self._normalise_timestamp_date
        )
        df["fileModificationDate"] = df["stat"].apply(lambda x: x.st_mtime)
        df["fileModificationDate"] = df["fileModificationDate"].apply(
            self._normalise_timestamp_date
        )
        df["MD5"] = df["fileOriginalPath"].apply(self._get_md5)
        df["fileSizeBytes"] = df["SIZE"].astype(str)
        return df

    def _normalise_physical_path(self, path: str) -> str:
        "Normalise and update volume letter to match DROID reports."
        return self._tidy_path(path)

    def _normalise_file_original_name(self, path: str) -> str:
        return os.path.basename(path)

    def _normalise_file_original_path(self, path: str, data_path: str) -> str:
        return path.replace(data_path, "")

    def _normalise_timestamp_date(self, date: str) -> str:
        return datetime.fromtimestamp(date).strftime("%Y-%m-%dT%H:%M:%S")

    def _get_md5(self, x: str) -> str:
        return self.checksums.get(x)

    def load_bag_info(self) -> dict:
        bag_info = {}
        with open(os.path.join(self.manifest_dir, "bag-info.txt"), "r") as f:
            for line in f:
                k, v = line.split(": ", 1)
                v = v.replace("\n", "")
                if k not in bag_info.keys():
                    bag_info.update({k: [v]})
                else:
                    current = bag_info.get(k)
                    current.append(v)
                    bag_info.update({k: current})
        return bag_info

    def load_file_checksums(self) -> dict:
        files = {}
        data_path = os.path.normpath("data")
        with open(os.path.join(self.manifest_dir, "manifest-md5.txt"), "r") as f:
            for line in f:
                v, k = line.split("  ", 1)
                k = k.replace("\n", "")
                k = k.replace(data_path, "", 1)
                k = os.path.normpath(k)
                files.update({k: v})
        return files
