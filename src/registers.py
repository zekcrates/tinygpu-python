class Register:
    def __init__(self):
        self.registers = [0] * 16 
        
    def set_readonly(self,block_id, block_dim, thread_id):
        self.registers[13] = block_id
        self.registers[14]  = block_dim
        self.registers[15] = thread_id

    def read(self, rs_addr, rt_addr):
        return (self.registers[rs_addr] , self.registers[rt_addr])

    def write(self, rd_addr, value) :
        if rd_addr >= 13 :
            return 
        self.registers[rd_addr] = value 

    