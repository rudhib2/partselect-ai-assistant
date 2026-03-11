import json
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "compatibility.json"


def load_compatibility():
    with open(DATA_PATH, "r") as f:
        return json.load(f)


def check_compatibility(part_number: str, model_number: str):
    compatibility_data = load_compatibility()

    part_number = part_number.strip().upper()
    model_number = model_number.strip().upper()

    compatible_models = compatibility_data.get(part_number, [])

    return {
        "part_number": part_number,
        "model_number": model_number,
        "compatible": model_number in compatible_models,
        "compatible_models": compatible_models
    }