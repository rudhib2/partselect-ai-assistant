import json
from pathlib import Path
from typing import Optional
from difflib import get_close_matches


DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "products.json"

STOP_WORDS = {
    "find",
    "show",
    "need",
    "looking",
    "for",
    "a",
    "an",
    "the",
    "my",
    "me",
    "please",
    "can",
    "you",
    "do",
    "i",
    "sell",
    "have"
}


def load_products():
    with open(DATA_PATH, "r") as f:
        return json.load(f)


def normalize_query(query: str):
    words = query.lower().strip().replace("?", "").replace(",", "").split()
    return [word for word in words if word not in STOP_WORDS]


def word_matches_searchable_text(word: str, searchable_words: set) -> bool:
    if word in searchable_words:
        return True

    close_matches = get_close_matches(word, list(searchable_words), n=1, cutoff=0.85)
    return len(close_matches) > 0


def search_parts(query: str, appliance_type: Optional[str] = None):
    products = load_products()
    normalized_words = normalize_query(query)

    results = []

    for product in products:
        if appliance_type and product.get("appliance", "").lower() != appliance_type.lower():
            continue

        searchable_text = " ".join(
            [
                product.get("part_number", ""),
                product.get("name", ""),
                product.get("description", ""),
                product.get("brand", ""),
                product.get("appliance", "")
            ]
        ).lower()

        searchable_words = set(
            searchable_text.replace(".", "").replace(",", "").split()
        )

        if product.get("part_number", "").lower() == query.lower().strip():
            results.append(product)
            continue

        if not normalized_words:
            continue

        match_count = sum(
            1 for word in normalized_words if word_matches_searchable_text(word, searchable_words)
        )

        # stricter precision:
        # - 1-word query: must match that 1 word
        # - 2-word query: both words must match
        # - 3+ words: allow one miss at most
        required_matches = len(normalized_words) if len(normalized_words) <= 2 else len(normalized_words) - 1

        if match_count >= required_matches:
            results.append(product)

    return results