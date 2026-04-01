from app.llm import extract_with_llm


def parse_user_input(message: str):

    message_lower = message.lower().strip()

    parsed = {
        "intent": None,
        "device_scope": None,
        "issue_type": None,
        "already_rebooted": None,
    }

    # Intent detection
    if any(word in message_lower for word in ["hi", "hello", "hey"]):
        parsed["intent"] = "greeting"

    elif any(word in message_lower for word in [
        "wifi", "internet", "connection", "network"
    ]):
        parsed["intent"] = "wifi_issue"

    # Handle direct short answers
    if message_lower in ["one", "single", "only", "just me"]:
        parsed["device_scope"] = "single_device"

    elif message_lower in ["multiple", "many", "all", "everything"]:
        parsed["device_scope"] = "multiple_devices"

    elif any(word in message_lower for word in [
        "all devices", "multiple devices", "many devices", "every device"
    ]):
        parsed["device_scope"] = "multiple_devices"

    elif any(word in message_lower for word in [
        "one device", "single device", "only device", "just one device"
    ]):
        parsed["device_scope"] = "single_device"

    elif any(phrase in message_lower for phrase in [
        "my phone", "my laptop", "my computer", "my tablet"
    ]):
        parsed["device_scope"] = "single_device"

    # Issue type
    if any(word in message_lower for word in [
        "not working", "no internet", "down", "offline"
    ]):
        parsed["issue_type"] = "outage"

    elif any(word in message_lower for word in [
        "slow", "lag", "very slow", "speed"
    ]):
        parsed["issue_type"] = "slow"

    elif any(word in message_lower for word in [
        "disconnect", "dropping", "intermittent", "unstable"
    ]):
        parsed["issue_type"] = "intermittent"

    # Already rebooted
    if any(word in message_lower for word in [
        "already restarted", "already rebooted", "i rebooted", "i restarted",
        "yes i restarted", "yes i rebooted"
    ]):
        parsed["already_rebooted"] = "yes"

    elif any(word in message_lower for word in [
        "not yet", "haven't restarted", "didn't restart",
        "did not restart", "no i did not", "no i didn't",
        "i have not restarted"
    ]):
        parsed["already_rebooted"] = "no"

    # Handle simple direct answers (VERY IMPORTANT for conversation flow)
    elif message_lower in ["no", "nope", "nah"]:
        parsed["already_rebooted"] = "no"

    elif message_lower in ["yes", "yeah", "yep"]:
        parsed["already_rebooted"] = "yes"

    # Always allow LLM to refine missing fields
    llm_result = {}

    # Call LLM only when device_scope is missing
    if parsed.get("device_scope") is None:
        llm_result = extract_with_llm(message)

    for key, value in llm_result.items():
        if key in parsed:

            
            if key == "device_scope" and parsed.get("device_scope") is not None:
                continue

            # Only fill missing values
            if parsed[key] is None and value is not None:
                parsed[key] = value

    # Debug log
    print("[PARSER FINAL]:", parsed)

    return parsed


def is_sufficient(parsed):
    return (
        parsed.get("device_scope") is not None and
        parsed.get("issue_type") is not None and
        parsed.get("already_rebooted") is not None
    )