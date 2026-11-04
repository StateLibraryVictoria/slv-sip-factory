import os
import argparse
import logging
import json
import pandas as pd
from src.bag_inventory import BagInventory

output_path = os.getenv("OUTPUT_PATH")
input_path = os.getenv("INPUT_PATH")
decode_uri = True


def build_decision_inventory_json(df: pd.DataFrame, creator: str, process: str):
    usecols = ["URI", "TYPE", "DECISION", "REASON", "SYSTEM", "SYSTEM_ID"]
    cols = df.columns
    for c in ["SYSTEM", "SYSTEM_ID"]:
        if c not in cols:
            df[c] = ""
    for c in cols:
        if c not in usecols:
            df = df.drop([c], axis=1)
    bi = BagInventory(df, "data\\")
    if not bi.validate(description=False):
        logging.info(f"Inventory failed validation.")
        print("Decision inventory could not be validated. See logfile for details.")
        return None
    metadata = bi.get_inventory_metadata(creator=creator, process=process)
    inventory = bi.get_decision_inventory()
    data = {}
    data.update({"script_information": metadata})
    data.update(inventory)
    return data


def main():
    def is_debugging() -> bool:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--debug",
            action="store_true",
            default=False,
            help="set logging level to debug",
        )
        debug_status = parser.parse_args()
        return debug_status.debug

    logging.debug("Running")
    files = [x for x in os.listdir(input_path) if x.endswith(".csv")]
    if len(files) == 0:
        logging.info("No files staged")
        return
    logging.debug(f"Loading files: {files}")
    for file in files:
        filepath = os.path.join(input_path, file)
        df = pd.read_csv(filepath, usecols=["URI", "TYPE", "DECISION", "REASON"])
        bi = BagInventory(df, "data\\")
        data = bi.get_decision_inventory()

        output_subfolder = os.path.join(output_path, os.path.splitext(file)[0])
        if not os.path.exists(output_subfolder):
            os.mkdir(output_subfolder)

        json_path = os.path.join(output_subfolder, "decisions.json")

        with open(json_path, "w") as f:
            json.dump(data, f, indent=4)


if __name__ == "__main__":
    main()
