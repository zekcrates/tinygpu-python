from thread import Thread 
from scheduler import Scheduler
from fetcher import Fetcher
from decoder import Decoder
class Core:
    def __init__(self):
        self.scheduler = Scheduler()
        self.fetcher = Fetcher()
        self.decoder = Decoder()
        self.threads = [Thread(i) for i in range(4)]

    def step(self, program_memory, data_memory):
        lsu_done = all(t.lsu.state == "IDLE" for t in self.threads)

        branch_taken = False
        branch_target = 0
        # previous instruction check 
        if self.decoder.is_branch:
            cond = self.decoder.get_branch_condition()
            thread_nzp = self.threads[0].pc.nzp
            branch_taken = any(thread_nzp.get(c, False) for c in cond)
            branch_target = self.decoder.immediate

        self.scheduler.step(self.fetcher.state == "FETCHED", lsu_done, self.decoder.is_ret,
                           branch_taken, branch_target)

        # fetch the instruction
        if self.fetcher.mem_read_valid and self.fetcher.mem_read_address < len(program_memory):
            self.fetcher.mem_read_ready = 1
            # get the instruction 
            self.fetcher.mem_read_data = program_memory[self.fetcher.mem_read_address]
        else:
            self.fetcher.mem_read_ready = 0

        self.fetcher.step(self.scheduler.core_state, self.scheduler.current_pc)

        #decode the instruction
        self.decoder.decode(self.fetcher.instruction)


        #execute the instruction
    
        for thread in self.threads:
            thread.step(self.scheduler.core_state, self.decoder)

        for thread in self.threads:
            lsu = thread.lsu
            if lsu.state == "REQUESTING":
                if lsu.mem_read_valid == 1:
                    if 0 <= lsu.mem_read_address < len(data_memory):
                        lsu.mem_read_data = data_memory[lsu.mem_read_address]
                        lsu.lsu_out = data_memory[lsu.mem_read_address]
                        lsu.mem_read_ready = 1
                    lsu.mem_read_valid = 0
                    lsu.state = "WAITING"
                elif lsu.mem_write_valid == 1:
                    if 0 <= lsu.mem_write_address < len(data_memory):
                        data_memory[lsu.mem_write_address] = lsu.mem_write_data
                    lsu.mem_write_valid = 0
                    lsu.mem_write_ready = 1
                    lsu.state = "WAITING"
            elif lsu.state == "WAITING":
                lsu.state = "DONE"
            elif lsu.state == "DONE":
                lsu.state = "IDLE"

        return self.scheduler.core_state == "DONE"