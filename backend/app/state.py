class ConversationState:

    def __init__(self):

        # FLOW
        self.stage = "qualifying"

        # SIGNALS
        self.device_scope = None
        self.issue_type = None        
        self.already_rebooted = None

    def to_dict(self):
        return {
            "stage": self.stage,
            "device_scope": self.device_scope,
            "issue_type": self.issue_type,  
            "already_rebooted": self.already_rebooted,
        }