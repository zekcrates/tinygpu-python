

class Fetcher:
    def __init__(self):
        self.state = "IDLE"
        self.mem_read_valid = 0
        self.mem_read_address = None
        self.mem_read_data = None
        self.mem_read_ready = 0
        self.instruction = None 

    def step(self, core_state, pc):
        if self.state == "IDLE":
            if core_state == "FETCH":
                self.state = "FETCHING"
                self.mem_read_valid = 1
                self.mem_read_address = pc

        elif self.state == "FETCHING":
            if self.mem_read_ready == 1:
                # mem_read_data comes from core.py (29-31)
                self.instruction = self.mem_read_data
                self.mem_read_valid = 0
                self.state = "FETCHED"

        elif self.state == "FETCHED":
            if core_state == "DECODE":
                self.state = "IDLE"
