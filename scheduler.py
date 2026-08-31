class Scheduler:
    def __init__(self):
        self.core_state = "IDLE"
        self.current_pc = 0 
    def step(self, fetch_done, lsu_done, is_ret, branch_taken=False, branch_target=0):
        if self.core_state == "IDLE":
            self.core_state = "FETCH"
        elif self.core_state == "FETCH":
            if fetch_done:
                self.core_state = "DECODE"
        elif self.core_state == "DECODE":
            self.core_state = "REQUEST"
        elif self.core_state == "REQUEST":
            self.core_state = "WAIT"
        elif self.core_state == "WAIT":
            if lsu_done:
                self.core_state = "EXECUTE"
        elif self.core_state == "EXECUTE":
            self.core_state = "UPDATE"
        elif self.core_state == "UPDATE":
            if is_ret:
                self.core_state = "DONE"
            else:
                self.core_state = "FETCH"
                if branch_taken:
                    self.current_pc = branch_target
                else:
                    self.current_pc+=1 
        return self.core_state 