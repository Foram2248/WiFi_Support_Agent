def evaluate_reboot_need(state):

    # Require more info
    if (
        state.device_scope is None or
        state.issue_type is None or
        state.already_rebooted is None
    ):
        return "need_more_info"

    # No conditions
    # Single device → unlikely router issue
    if state.device_scope == "single_device":
        return "no"

    # Already rebooted → avoid repeating
    if state.already_rebooted == "yes":
        return "no"


    # Yes conditions
    # Multiple devices + outage/slow/intermittent + not rebooted
    if (
        state.device_scope == "multiple_devices" and
        state.already_rebooted == "no"
    ):
        return "yes"

    # Fallback
    return "need_more_info"