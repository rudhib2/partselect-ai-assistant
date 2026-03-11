import json
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "troubleshooting.json"


def load_troubleshooting_data():
    with open(DATA_PATH, "r") as f:
        return json.load(f)


def get_troubleshooting_guide(appliance: str, symptom: str):
    troubleshooting_data = load_troubleshooting_data()

    appliance = appliance.lower().strip()
    symptom = symptom.lower().strip()

    exact_match = None
    partial_matches = []

    for entry in troubleshooting_data:
        entry_appliance = entry.get("appliance", "").lower()
        entry_symptom = entry.get("symptom", "").lower()

        if entry_appliance != appliance:
            continue

        if entry_symptom == symptom:
            exact_match = entry
            break

        if symptom in entry_symptom or entry_symptom in symptom:
            partial_matches.append(entry)

    if exact_match:
        return {
            "match_type": "exact",
            "result": exact_match
        }

    if partial_matches:
        return {
            "match_type": "partial",
            "result": partial_matches
        }

    return {
        "match_type": "none",
        "result": []
    }