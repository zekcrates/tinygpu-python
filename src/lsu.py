
class LoadStoreUnit:
    def __init__(self):
        self.state = "IDLE"
        self.lsu_out = 0 
        self.mem_read_valid = 0
        self.mem_read_address = -1
        self.mem_read_ready  = 0
        self.mem_read_data  = None 
        self.mem_write_valid  = 0
        self.mem_write_address = -1
        self.mem_write_data = -1
        self.mem_write_ready = 0

    def step(self, core_state, is_load, is_store, rs, rt):
        if self.state == "IDLE":
            if core_state == "REQUEST":
                if is_load:
                    self.state = "REQUESTING"
                    self.mem_read_valid = 1
                    self.mem_read_address = rs
                elif is_store:
                    self.state = "REQUESTING"
                    self.mem_write_valid = 1
                    self.mem_write_address = rs
                    self.mem_write_data = rt

        elif self.state == "REQUESTING":
            if is_load and self.mem_read_ready == 1:
                self.lsu_out = self.mem_read_data
                self.mem_read_valid = 0
                self.state = "WAITING"
            elif is_store and self.mem_write_ready == 1:
                self.mem_write_valid = 0
                self.state = "WAITING"
