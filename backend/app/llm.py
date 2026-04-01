import os
from openai import OpenAI
import json
from dotenv import load_dotenv
from pathlib import Path

# load .env
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def call_llm(prompt: str, temperature=0.3):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("[LLM ERROR]:", str(e))
        return None

# Extraction
def extract_with_llm(message: str):

    prompt = f"""
You are an information extraction system.

Extract ONLY these fields from the user message.

Return STRICT JSON only:

{{
  "device_scope": "single_device" | "multiple_devices" | null,
  "issue_type": "outage" | "slow" | "intermittent" | null,
  "already_rebooted": "yes" | "no" | null
}}

RULES:
- Use clear user intent when obvious
- Avoid guessing when unclear
- Prefer null if ambiguous
- Do NOT infer beyond user message

- "multiple_devices" if more than one device affected
- "single_device" if only one device
- "outage" if internet not working at all
- "slow" if speed is low
- "intermittent" if disconnecting / unstable
- rebooted = yes if user says restarted router
- rebooted = no if user says not restarted
- If unclear → null

User message:
"{message}"
"""

    result = call_llm(prompt, temperature=0)

    if result:
        try:
            return json.loads(result)
        except Exception:
            return {}

    return {}


# Yes / No detection
def detect_yes_no_llm(message: str):

    msg = message.lower().strip()

    # FIX: rule-based first
    if msg in ["yes", "yeah", "yep"]:
        return "yes"

    if msg in ["no", "nope", "nah"]:
        return "no"

    # fallback to LLM
    prompt = f"""
Classify the user response into:

- "yes"
- "no"
- "unclear"

Return ONLY one word.

User message:
"{message}"
"""

    result = call_llm(prompt, temperature=0)

    if result:
        result = result.lower().strip()
        if result in ["yes", "no", "unclear"]:
            return result

    return "unclear"


# Vague query - # Optional helpers for future improvements
def is_unclear_response(message: str):

    msg = message.lower().strip()

    # FIX: rule-based first
    if msg in ["idk", "maybe", "not sure", "what", "?", "huh"]:
        return "unclear"

    prompt = f"""
Determine if this user message is unclear, vague, or ambiguous.

Return ONLY:
- "clear"
- "unclear"

User message:
"{message}"
"""

    result = call_llm(prompt, temperature=0)

    if result and result.lower().strip() in ["clear", "unclear"]:
        return result.lower().strip()

    return "clear"


# Reboot intent
def classify_reboot_intent(message: str):
    """
    Lightweight intent detection during reboot flow.
    Keep rule-based for reliability.
    """

    msg = message.lower().strip()

    # FIX: expanded rule coverage
    if any(word in msg for word in ["done", "i did", "completed", "finished", "yes done"]):
        return "done"

    if msg in ["next", "ok"]:
        return "done"

    if msg in ["skip"]:
        return "skip"

    if msg in ["cancel", "stop"]:
        return "cancel"

    if "?" in msg:
        return "clarification"

    # fallback to LLM only if unclear
    prompt = f"""
Classify the user response during a router reboot process.

Return ONLY one of:
- "done"
- "skip"
- "cancel"
- "clarification"
- "unrelated"

User message:
"{message}"
"""

    result = call_llm(prompt, temperature=0)

    if result:
        result = result.lower().strip()
        if result in ["done", "skip", "cancel", "clarification", "unrelated"]:
            return result

    return "unrelated"


# Response polishing
def rewrite_response(text: str):

    # FIX: Avoid unnecessary LLM calls for simple responses
    if len(text) < 120:
        return text

    prompt = f"""
Rewrite the message below to be clear, natural, and professional.

Do NOT change meaning.
Keep it concise.

Message:
"{text}"
"""

    result = call_llm(prompt, temperature=0.2)

    return result if result else text


# Question generation - # Optional helpers for future improvements
def generate_question(question_type: str):

    base_map = {
        "device_scope": "Is the issue happening on just one device, or on multiple devices?",
        "issue_type": "Is your internet completely down, very slow, or dropping in and out?",
        "already_rebooted": "Have you already tried restarting your router recently?"
    }

    return base_map.get(question_type, "Can you provide more details?")