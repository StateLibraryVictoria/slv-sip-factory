import pandas as pd
import logging


class DecisionNormaliser:
    def __init__(self):
        self

    def normalise(self, df: pd.DataFrame) -> pd.DataFrame:
        df.columns = df.columns.str.upper()
        for col in df.columns:
            df[col] = df[col].astype(str)
            df[col] = df[col].fillna("")
            if col in ["DECISION", "SYSTEM"]:
                df[col] = df[col].str.lower()
                df[col] = df[col].str.strip()
        return df

    def fix_blank_dispose_decisions(
        self, df: pd.DataFrame, reason: str = "Not selected."
    ) -> pd.DataFrame:
        if "REASON" not in df.columns:
            df["REASON"] = ""
        df = self.normalise(df)
        df.loc[(df.DECISION == "dispose") & (df.REASON == ""), "REASON"] = reason
        logging.error(df.head())
        return df

    def replace_decision(self, df: pd.DataFrame, old_decision: str, new_decision: str):
        df.loc[df.DECISION == old_decision, "DECISION"] = new_decision
        return df

    # replace decision and reason
    def update_decision_reason(
        self, df: pd.DataFrame, decision: str, new_reason: str
    ) -> pd.DataFrame:
        df.loc[df.DECISION == decision, "REASON"] = new_reason
        return df
