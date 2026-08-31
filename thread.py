from registers import Register
from alu import Alu
from pc import PC
from lsu import LoadStoreUnit


class Thread:
    def __init__(self, thread_id):
        self.thread_id = thread_id
        self.registers = Register()
        self.alu = Alu()
        self.pc = PC()
        self.lsu = LoadStoreUnit()
        self.rs = 0
        self.rt = 0
        self.alu_out = 0

    def step(self, core_state, decoder):
        if core_state == "REQUEST":
            self.rs, self.rt = self.registers.read(decoder.rs, decoder.rt)
            self.lsu.step(core_state, decoder.is_load, decoder.is_store,
                         self.rs, self.rt)

        elif core_state == "EXECUTE":
            if decoder.is_compare:
                self.alu_out = self.alu.execute("CMP", self.rs, self.rt)
            elif decoder.write_to_register:
                self.alu_out = self.alu.execute(decoder.alu_op, self.rs, self.rt)
            self.lsu.step(core_state, decoder.is_load, decoder.is_store,
                         self.rs, self.rt)

        elif core_state == "UPDATE":
            if decoder.write_to_register:
                if decoder.is_const:
                    self.registers.write(decoder.rd, decoder.immediate)
                elif decoder.is_load:
                    self.registers.write(decoder.rd, self.lsu.lsu_out)
                else:
                    self.registers.write(decoder.rd, self.alu_out)

            if decoder.is_compare:
                # self.alu_out = (t/f,t/f,t/f)
                self.pc.nzp = {
                    'N': self.alu_out[0], 
                    'Z': self.alu_out[1],
                    'P': self.alu_out[2],
                }

            if decoder.is_branch:
                cond = decoder.get_branch_condition()
                taken = any(self.pc.nzp.get(c, False) for c in cond)
                if taken:
                    self.pc.current_pc = decoder.immediate
                else:
                    self.pc.current_pc += 1
            else:
                self.pc.current_pc += 1

            self.lsu.step(core_state, decoder.is_load, decoder.is_store,
                         self.rs, self.rt)
