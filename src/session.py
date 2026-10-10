class Session:
    def __init__(self):
        self.role = "Customer"
        self.customer_id = ""
        self.history = []
        self.active_booking_id = None
        self.authenticated = False
        self.agent_name = None
        
    def reset(self):
        self.history = []
        self.active_booking_id = None
        
    def hard_reset(self):
        self.customer_id = ""
        self.history = []
        self.active_booking_id = None
        self.authenticated = False
        self.agent_name = None
