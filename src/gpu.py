from .dcr import DeviceControlRegister
from .core import Core
from .dispatcher import Dispatcher



class GPU:
    def __init__(self, num_cores=2, threads_per_block=4, memory_size=256):

        self.dcr= DeviceControlRegister()
        self.dispatcher = Dispatcher(num_cores, threads_per_block)
        self.cores = [Core() for _ in range(num_cores)]
        self.program_memory = [0] * memory_size
        self.data_memory = [0] * memory_size

    def load_program(self, instructions):
        for i, instr in enumerate(instructions):
            self.program_memory[i] = instr

    def load_data(self,data):
        for i, val in enumerate(data):
            self.data_memory[i] = val 

    def run(self, num_threads):

        self.dcr.set_thread_count(num_threads)
        cycles =0

        while True :
            core_done= []
            for core in self.cores:
                done = core.step(self.program_memory, self.data_memory)
                core_done.append(done)
            all_done, dispatched = self.dispatcher.step(
                self.dcr.get_thread_count(), core_done
            )

            for core_idx, block_idx in dispatched:
                core = self.cores[core_idx]
                core.scheduler.current_pc = 0
                core.scheduler.core_state = "IDLE"
                core.fetcher.state = "IDLE"
                core.fetcher.mem_read_valid = 0
                core.fetcher.mem_read_address = None
                core.fetcher.instruction = None
                core.decoder.is_ret = False
                for t in range(self.dispatcher.threads_per_block):
                    core.threads[t].registers.set_readonly(
                        block_idx, self.dispatcher.threads_per_block, t
                    )

            cycles += 1
            if all_done:
                break

        return self.data_memory, cycles

    def step(self, program_memory=None, data_memory=None):
        """Advance the whole device by one clock cycle.

        Keeping this operation on the GPU (rather than in the Flask app) makes
        the visualizer use exactly the same dispatch behaviour as ``run``.
        """
        program_memory = self.program_memory if program_memory is None else program_memory
        data_memory = self.data_memory if data_memory is None else data_memory

        core_done = [core.step(program_memory, data_memory) for core in self.cores]
        all_done, dispatched = self.dispatcher.step(
            self.dcr.get_thread_count(), core_done
        )

        for core_idx, block_idx in dispatched:
            core = self.cores[core_idx]
            core.scheduler.current_pc = 0
            core.scheduler.core_state = "IDLE"
            core.fetcher.state = "IDLE"
            core.fetcher.mem_read_valid = 0
            core.fetcher.mem_read_address = None
            core.fetcher.mem_read_data = None
            core.fetcher.instruction = None
            core.decoder.is_ret = False
            for thread_idx in range(self.dispatcher.threads_per_block):
                core.threads[thread_idx].registers.set_readonly(
                    block_idx, self.dispatcher.threads_per_block, thread_idx
                )

        return all_done
