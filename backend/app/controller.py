from app.decision import evaluate_reboot_need
from app.llm import (
    rewrite_response,
    detect_yes_no_llm,
    classify_reboot_intent,
)

# Extracted pdf steps
REBOOT_STEPS = [
    "Unplug the power cable from both your router and modem.",
    "Wait for about 10 seconds.",
    "Plug the modem back in and wait until its online light stops blinking (about 2 minutes).",
    "Plug the router back in.",
    "Wait until the router’s power light stops blinking, then wait another 2 minutes before testing your internet."
]

def handle_user_input(state, parsed_input):

    raw_message = parsed_input.get("raw_message", "").lower()

    # Handle greeting
    if parsed_input.get("intent") == "greeting":
        return rewrite_response("Hi! Is your WiFi not working or just slow?")

    # Handle out-of-scope / irrelevant queries
    if (
        parsed_input.get("intent") is None and
        parsed_input.get("device_scope") is None and
        parsed_input.get("issue_type") is None and
        parsed_input.get("already_rebooted") is None and 
        state.stage == "qualifying"
    ):
        return rewrite_response(
            "I’m here to help with WiFi or internet connectivity issues. "
            "Please describe your connection problem so I can assist you."
        )

    # STEP 1: Update state
    if parsed_input.get("device_scope"):
        state.device_scope = parsed_input["device_scope"]

    if parsed_input.get("issue_type"):
        state.issue_type = parsed_input["issue_type"]

    if parsed_input.get("already_rebooted"):
        state.already_rebooted = parsed_input["already_rebooted"]

    # STEP 2: Qualifying     
    if state.stage == "qualifying":

        # Don't ask again if already known
        if state.device_scope is None:
            return rewrite_response("Is this happening on one device or multiple devices?")

        if state.issue_type is None:
            return rewrite_response("Is the issue that your internet is slow, completely down, or keeps disconnecting?")

        if state.device_scope == "single_device":
            state.stage = "end"
            state.end_reason = "not_applicable"
            return rewrite_response(
                "Since this is affecting only one device, a router reboot isn’t necessary. " \
                "This likely needs troubleshooting on the device itself. " \
                "You can start a new chat anytime if you need help with something else."
            )

        if state.already_rebooted is None:
            return rewrite_response("Have you already tried restarting your router?")

        # safety guard
        if not (
            state.device_scope and
            state.issue_type and
            state.already_rebooted
        ):
            return rewrite_response("Let me gather a bit more information before suggesting a fix.")

        # decision
        decision = evaluate_reboot_need(state)

        if decision == "no":
            state.stage = "end"
            return rewrite_response(
                "Since you've already tried restarting the router and the issue is still affecting everything, a reboot is unlikely to fix this. " \
                "Sorry about that. This may be an issue with your internet service, so you may need to contact your service provider for further help. " \
                "You can start a new chat anytime if you need assistance with something else."
            )

        if decision == "yes":
            state.stage = "reboot_intro"
            return rewrite_response(
                "It looks like a router restart could help. I’ll guide you step by step."
            )

    # STEP 3: Start reboot flow
    if state.stage == "reboot_intro":
        state.stage = "reboot_steps"
        state.reboot_step_index = 0
        state.awaiting_confirmation = False
        return format_step(state.reboot_step_index)

    # STEP 4: Step execution
    if state.stage == "reboot_steps":

        intent = classify_reboot_intent(raw_message)

        # --- confirmation handling ---
        if getattr(state, "awaiting_confirmation", False):
            answer = detect_yes_no_llm(raw_message)

            if answer == "yes":
                state.awaiting_confirmation = False
                state.reboot_step_index += 1

                if state.reboot_step_index < len(REBOOT_STEPS):
                    return format_step(state.reboot_step_index)
                else:
                    state.stage = "post_check"
                    return rewrite_response("All steps are done. Did this fix your issue? (yes/no)")

            elif answer == "no":
                return rewrite_response(
                    f"No problem, please complete this step first:\n\n{format_step(state.reboot_step_index)}"
                )

            else:
                return rewrite_response("Just to confirm — did you complete that step? (yes/no)")

        if intent == "cancel":
            state.stage = "end"
            return rewrite_response("No problem — we can stop here. Let me know if you need help later.")

        if intent == "clarification":
            return rewrite_response(
                f"You're currently on Step {state.reboot_step_index + 1}: {REBOOT_STEPS[state.reboot_step_index]}\n\n"
                "Let me know once you're done."
            )

        if intent == "unrelated":
            return rewrite_response(
                f"Let's finish this step first.\n\n{format_step(state.reboot_step_index)}"
            )

        if intent == "done":

            # only validate first step
            if state.reboot_step_index == 0:
                state.awaiting_confirmation = True
                return rewrite_response(
                    "Just to confirm — did you unplug both the router and modem? (yes/no)"
                )

            state.reboot_step_index += 1

            if state.reboot_step_index < len(REBOOT_STEPS):
                return format_step(state.reboot_step_index)
            else:
                state.stage = "post_check"
                return rewrite_response("All steps are done. Did this fix your issue? (yes/no)")


        if intent == "skip":
            state.awaiting_confirmation = True
            return rewrite_response(
                f"It’s important to complete this step for the reboot to work properly.\n\n"
                f"Did you complete this step?\n\n{format_step(state.reboot_step_index)} (yes/no)"
            )

        return rewrite_response(
            f"Please complete this step first.\n\n{format_step(state.reboot_step_index)}"
        )

    # STEP 5: Post check 
    if state.stage == "post_check":

        answer = detect_yes_no_llm(raw_message)

        if answer == "yes":
            state.stage = "end"
            state.end_reason = "resolved"
            return rewrite_response(
                "Great — glad everything’s working again! If you run into any other issues, feel free to start a new chat anytime."
            )

        elif answer == "no":
            state.stage = "end"
            state.end_reason = "not_resolved"
            return rewrite_response(
                "Sorry that didn’t resolve the issue. This may require further investigation, so I recommend contacting your internet service provider for more advanced support."
            )

        else:
            return rewrite_response("Please answer with yes or no so I can help you properly.")

    # End
    if state.stage == "end":
        return rewrite_response(
            "This conversation has ended. Please start a new chat if you need further help."
        )

    # Fallback
    return rewrite_response("Something went wrong. Let's start again.")


def format_step(index):
    return f"Step {index + 1}: {REBOOT_STEPS[index]}"