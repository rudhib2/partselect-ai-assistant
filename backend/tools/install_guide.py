import json
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "install_guides.json"


def load_install_guides():
    with open(DATA_PATH, "r") as f:
        return json.load(f)


def get_install_guide(part_number: str):
    install_guides = load_install_guides()
    part_number = part_number.strip().upper()

    guide = install_guides.get(part_number)

    if not guide:
        return {
            "part_number": part_number,
            "found": False,
            "tools_needed": [],
            "steps": []
        }

    return {
        "part_number": part_number,
        "found": True,
        "tools_needed": guide.get("tools_needed", []),
        "steps": guide.get("steps", [])
    }