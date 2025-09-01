"""
Google Sheets Database Module
Handles reading and writing to the Diksha fundraising pipeline Google Sheet
"""

import os
from difflib import get_close_matches
from .google_auth import get_google_clients

class SheetsDB:
    def __init__(self):
        self.sheet_id = os.environ.get("MAIN_SHEET_ID")
        self.tab = os.environ.get("MAIN_SHEET_TAB", "Pipeline Tracker")
        self.sheets, _ = get_google_clients()

    def _fetch_rows(self):
        range_ = f"'{self.tab}'!A2:H"
        result = self.sheets.spreadsheets().values().get(
            spreadsheetId=self.sheet_id,
            range=range_
        ).execute()
        return result.get("values", [])

    def get_pipeline(self):
        rows = self._fetch_rows()
        stages = {}
        for r in rows:
            org = r[0] if len(r) > 0 else ""
            stage = r[4] if len(r) > 4 else "UNKNOWN"
            donor = {
                "organization": org,
                "contact": r[1] if len(r) > 1 else "",
                "email": r[2] if len(r) > 2 else "",
                "phone": r[3] if len(r) > 3 else "",
                "previous_stage": r[5] if len(r) > 5 else "",
                "sector_tags": r[6] if len(r) > 6 else "",
                "geography": r[7] if len(r) > 7 else ""
            }
            stages.setdefault(stage, []).append(donor)
        return stages

    def find_org(self, query):
        rows = self._fetch_rows()
        orgs = [r[0] for r in rows if len(r) > 0]
        match = get_close_matches(query, orgs, n=1, cutoff=0.5)
        if not match:
            return None
        for r in rows:
            if r[0] == match[0]:
                return {
                    "organization": r[0],
                    "contact": r[1] if len(r) > 1 else "",
                    "email": r[2] if len(r) > 2 else "",
                    "stage": r[4] if len(r) > 4 else "UNKNOWN"
                }
        return None
