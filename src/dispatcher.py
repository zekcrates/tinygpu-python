class Dispatcher:
    def __init__(self, num_cores, threads_per_block=4):
        self.num_cores = num_cores 
        self.threads_per_block = threads_per_block

        self.cores_free = [True] * num_cores

        self.blocks_dispatched = 0 


    def step(self, thread_count, core_done):
        total_blocks = (thread_count + self.threads_per_block - 1) // self.threads_per_block
        dispatched = []

        for i in range(self.num_cores):
            if core_done[i]:
                self.cores_free[i] = True 

            if self.cores_free[i] and self.blocks_dispatched < total_blocks:
                self.cores_free[i] = False 
                block_idx = self.blocks_dispatched
                self.blocks_dispatched +=1 
                dispatched.append((i, block_idx))

        done = self.blocks_dispatched >= total_blocks and all(self.cores_free)
        return done, dispatched