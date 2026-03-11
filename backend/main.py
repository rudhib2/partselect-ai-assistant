import os
import json
import time
from typing import Optional
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI

from tools.search_parts import search_parts
from tools.compatibility import check_compatibility
from tools.troubleshooting import get_troubleshooting_guide
from tools.install_guide import get_install_guide
from collections import Counter


load_dotenv()

last_part_number = None
INSIGHTS_LOG_PATH = Path(__file__).resolve().parent / "insights_log.json"

deepseek_client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SearchPartsRequest(BaseModel):
    query: str
    appliance_type: Optional[str] = None


class CompatibilityRequest(BaseModel):
    part_number: str
    model_number: str


class TroubleshootingRequest(BaseModel):
    appliance: str
    symptom: str


class InstallGuideRequest(BaseModel):
    part_number: str


class ChatRequest(BaseModel):
    message: str


def load_insights_log():
    if not INSIGHTS_LOG_PATH.exists():
        return []
    with open(INSIGHTS_LOG_PATH, "r") as f:
        return json.load(f)


def save_insights_log(events):
    with open(INSIGHTS_LOG_PATH, "w") as f:
        json.dump(events, f, indent=2)


def log_insight(event):
    events = load_insights_log()
    events.append(event)
    save_insights_log(events)

def compute_insights_summary():
    events = load_insights_log()

    if not events:
        return {
            "total_queries": 0,
            "intent_distribution": {},
            "appliance_distribution": {},
            "top_parts": [],
            "top_symptoms": [],
            "unavailable_queries": [],
            "average_response_time_ms": 0
        }

    intent_counter = Counter()
    appliance_counter = Counter()
    part_counter = Counter()
    symptom_counter = Counter()
    unavailable_counter = Counter()
    response_times = []

    for event in events:
        intent = event.get("intent")
        appliance = event.get("appliance_type")
        parts = event.get("returned_part_numbers", [])
        symptom = event.get("matched_symptom")
        response_time = event.get("response_time_ms")
        unavailable = event.get("unavailable_request")
        unavailable_query = event.get("unavailable_query")

        if intent:
            intent_counter[intent] += 1

        if appliance:
            appliance_counter[appliance] += 1

        for part in parts:
            part_counter[part] += 1

        if symptom:
            symptom_counter[symptom] += 1

        if unavailable and unavailable_query:
            unavailable_counter[unavailable_query] += 1

        if response_time is not None:
            response_times.append(response_time)

    avg_response_time = round(
        sum(response_times) / len(response_times),
        2
    ) if response_times else 0

    return {
        "total_queries": len(events),
        "intent_distribution": dict(intent_counter),
        "appliance_distribution": dict(appliance_counter),
        "top_parts": [
            {"part_number": part, "count": count}
            for part, count in part_counter.most_common(5)
        ],
        "top_symptoms": [
            {"symptom": symptom, "count": count}
            for symptom, count in symptom_counter.most_common(5)
        ],
        "top_unavailable_queries": [
            {"query": query, "count": count}
            for query, count in unavailable_counter.most_common(10)
        ],
        "average_response_time_ms": avg_response_time
    }

def extract_model_number(message: str):
    words = message.replace("?", "").replace(",", "").split()
    for word in words:
        upper_word = word.upper()
        if any(char.isdigit() for char in upper_word) and not upper_word.startswith("PS"):
            return upper_word
    return None


def detect_appliance_type(message: str):
    lowered = message.lower()
    if "dishwasher" in lowered:
        return "dishwasher"
    if "fridge" in lowered or "refrigerator" in lowered:
        return "refrigerator"
    return None


def classify_intent(message: str) -> str:
    system_prompt = """
You are an intent classifier for an appliance-parts assistant.

The assistant ONLY supports:
- refrigerator parts
- dishwasher parts
- part search
- compatibility checks
- troubleshooting help
- installation guidance

Return ONLY valid JSON in this exact format:
{"intent":"search"}

Allowed intent values:
- search
- compatibility
- troubleshoot
- install
- out_of_scope

Classification rules:
- search: user wants to find, browse, or buy a part/product
- compatibility: user asks if a part fits a model
- troubleshoot: user describes a problem/symptom with an appliance
- install: user asks how to install or replace a part
- out_of_scope: anything unrelated or unsupported

Important:
- "replacement wheel", "do you sell wheels", "show me an ice maker" are search
- vague but in-scope queries like "refrigerator" or "dishwasher parts" are search
- only return JSON
"""
    try:
        response = deepseek_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            response_format={"type": "json_object"},
            temperature=0
        )

        content = response.choices[0].message.content
        parsed = json.loads(content)
        intent = parsed.get("intent", "out_of_scope")

        if intent not in {"search", "compatibility", "troubleshoot", "install", "out_of_scope"}:
            return "out_of_scope"

        return intent
    except Exception:
        lowered = message.lower()
        if "compatible" in lowered or "fit" in lowered or "model" in lowered:
            return "compatibility"
        if "install" in lowered or "replace" in lowered:
            return "install"
        if any(
            phrase in lowered
            for phrase in [
                "not working",
                "leaking",
                "not cooling",
                "not draining",
                "broken",
                "not heating",
                "ice maker"
            ]
        ):
            return "troubleshoot"
        if any(
            phrase in lowered
            for phrase in [
                "find",
                "show",
                "need",
                "part",
                "wheel",
                "pump",
                "gasket"
            ]
        ):
            return "search"
        return "out_of_scope"


@app.get("/")
def root():
    return {"message": "Instalily case study backend is running"}


@app.get("/insights-log")
def insights_log_endpoint():
    return {"events": load_insights_log()}

@app.get("/insights-summary")
def insights_summary_endpoint():
    return compute_insights_summary()

@app.post("/search-parts")
def search_parts_endpoint(request: SearchPartsRequest):
    results = search_parts(request.query, request.appliance_type)
    return {"results": results}


@app.post("/check-compatibility")
def check_compatibility_endpoint(request: CompatibilityRequest):
    result = check_compatibility(request.part_number, request.model_number)
    return result


@app.post("/troubleshoot")
def troubleshoot_endpoint(request: TroubleshootingRequest):
    result = get_troubleshooting_guide(request.appliance, request.symptom)
    return result


@app.post("/install-guide")
def install_guide_endpoint(request: InstallGuideRequest):
    result = get_install_guide(request.part_number)
    return result


@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    global last_part_number

    start_time = time.time()
    message = request.message.strip()
    lowered = message.lower()
    intent = classify_intent(message)

    appliance_type = detect_appliance_type(message)
    model_number = extract_model_number(message)
    used_memory = False
    success = False
    matched_symptom = None
    returned_part_numbers = []
    unavailable_request = False
    unavailable_query = None

    response_payload = None

    if intent == "compatibility":
        words = message.replace("?", "").replace(",", "").split()
        part_number = None

        for word in words:
            upper_word = word.upper()
            if upper_word.startswith("PS"):
                part_number = upper_word
                break

        if not part_number and last_part_number:
            part_number = last_part_number
            used_memory = True

        if not part_number or not model_number:
            response_payload = {
                "intent": "compatibility",
                "answer": "Please provide both a part number and appliance model number so I can check compatibility."
            }
        else:
            result = check_compatibility(part_number, model_number)
            success = True
            returned_part_numbers = [part_number]

            if result["compatible"]:
                answer = f"Yes — part {part_number} is compatible with model {model_number}."
            else:
                answer = f"No — part {part_number} is not listed as compatible with model {model_number}."

            response_payload = {
                "intent": "compatibility",
                "answer": answer,
                "data": result
            }

    elif intent == "install":
        words = message.replace("?", "").replace(",", "").split()
        part_number = None

        for word in words:
            upper_word = word.upper()
            if upper_word.startswith("PS"):
                part_number = upper_word
                break

        if not part_number and last_part_number:
            part_number = last_part_number
            used_memory = True

        if not part_number:
            response_payload = {
                "intent": "install",
                "answer": "Please provide the part number so I can show installation steps."
            }
        else:
            result = get_install_guide(part_number)
            returned_part_numbers = [part_number]
            success = result["found"]

            if not result["found"]:
                response_payload = {
                    "intent": "install",
                    "answer": f"I couldn’t find installation instructions for part {part_number}.",
                    "data": result
                }
            else:
                steps_text = "\n".join([f"{i + 1}. {step}" for i, step in enumerate(result["steps"])])
                tools_text = ", ".join(result["tools_needed"]) if result["tools_needed"] else "No special tools listed"

                answer = (
                    f"Here are the installation steps for {part_number}.\n\n"
                    f"Tools needed: {tools_text}\n\n"
                    f"{steps_text}"
                )

                response_payload = {
                    "intent": "install",
                    "answer": answer,
                    "data": result
                }

    elif intent == "troubleshoot":
        symptom_candidates = [
            "ice maker not working",
            "refrigerator not cooling",
            "freezer too cold refrigerator warm",
            "water dispenser not working",
            "frost buildup in freezer",
            "refrigerator runs constantly",
            "refrigerator light not working",
            "ice maker leaking",
            "dishwasher not draining",
            "dishwasher leaking",
            "dishwasher not cleaning dishes",
            "dishwasher not heating",
            "dishwasher door will not latch",
            "dishwasher not filling with water",
            "dishwasher rack wheel broken",
            "dishwasher buttons not responding"
        ]

        if not appliance_type:
            response_payload = {
                "intent": "troubleshoot",
                "answer": "Please tell me whether this is a refrigerator or dishwasher issue."
            }
        else:
            for candidate in symptom_candidates:
                candidate_words = candidate.split()
                if all(word in lowered for word in candidate_words if word not in ["the", "with"]):
                    matched_symptom = candidate
                    break

            if not matched_symptom:
                for candidate in symptom_candidates:
                    if any(word in lowered for word in candidate.split()):
                        matched_symptom = candidate
                        break

            if not matched_symptom:
                response_payload = {
                    "intent": "troubleshoot",
                    "answer": "I couldn’t identify the exact symptom yet. Try describing the problem more specifically, like 'dishwasher leaking' or 'refrigerator not cooling'."
                }
            else:
                result = get_troubleshooting_guide(appliance_type, matched_symptom)
                success = result["match_type"] != "none"

                if result["match_type"] == "none":
                    response_payload = {
                        "intent": "troubleshoot",
                        "answer": "I couldn’t find a matching troubleshooting guide for that symptom yet."
                    }
                else:
                    entry = result["result"] if result["match_type"] == "exact" else result["result"][0]
                    returned_part_numbers = entry.get("recommended_parts", [])
                    causes = "\n".join([f"- {cause}" for cause in entry["possible_causes"]])
                    parts = ", ".join(entry["recommended_parts"])

                    answer = (
                        f"Here are some likely causes for this {appliance_type} issue:\n"
                        f"{causes}\n\n"
                        f"Recommended parts: {parts}"
                    )

                    response_payload = {
                        "intent": "troubleshoot",
                        "answer": answer,
                        "data": result
                    }

    elif intent == "search":
        results = search_parts(message, appliance_type)

        if results:
            last_part_number = results[0]["part_number"]
            success = True
        else:
            unavailable_request = True
            unavailable_query = message

        if not results:
            cleaned_query = message.strip().rstrip("?.!")
            lowered_query = cleaned_query.lower()

            prefixes = [
                "show me ",
                "find me ",
                "do you have ",
                "i need ",
                "can you find ",
                "looking for ",
                "get me "
            ]

            display_query = cleaned_query
            for prefix in prefixes:
                if lowered_query.startswith(prefix):
                    display_query = cleaned_query[len(prefix):].strip()
                    break

            if appliance_type and appliance_type not in display_query.lower():
                display_query = f"{appliance_type} {display_query}".strip()

            if appliance_type:
                response_payload = {
                    "intent": "search",
                    "answer": (
                        f"I couldn’t find a matching {display_query} in the current demo catalog. "
                        "Try searching with a model number, a specific part number, or a slightly different part name."
                    )
                }
            else:
                response_payload = {
                    "intent": "search",
                    "answer": (
                        f"I couldn’t find a matching part for '{cleaned_query}' in the current demo catalog. "
                        "Try including the appliance type, a model number, or a specific part number."
                    )
                }
        else:
            top_results = results[:3]
            returned_part_numbers = [item["part_number"] for item in top_results]
            lines = [
                f"{item['part_number']}: {item['name']} (${item['price']})"
                for item in top_results
            ]
            answer = "Here are the top matching parts:\n" + "\n".join(lines)

            response_payload = {
                "intent": "search",
                "answer": answer,
                "data": top_results
            }

    else:
        response_payload = {
            "intent": "out_of_scope",
            "answer": "I’m designed to help with refrigerator and dishwasher parts, compatibility checks, troubleshooting, and installation help."
        }

    elapsed_ms = round((time.time() - start_time) * 1000, 2)

    log_insight({
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "message": message,
        "intent": response_payload["intent"],
        "appliance_type": appliance_type,
        "model_number": model_number,
        "matched_symptom": matched_symptom,
        "returned_part_numbers": returned_part_numbers,
        "success": success,
        "response_time_ms": elapsed_ms,
        "used_memory": used_memory,
        "unavailable_request": unavailable_request,
        "unavailable_query": unavailable_query
    })

    return response_payload