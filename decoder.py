opcodes = {
    0b0000: "NOP",    # Do nothing
    0b0001: "BRnzp",  # Branch/jump to another instruction
    0b0010: "CMP",    # Compare two registers
    0b0011: "ADD",    # rd = rs + rt
    0b0100: "SUB",    # rd = rs - rt
    0b0101: "MUL",    # rd = rs * rt
    0b0110: "DIV",    # rd = rs / rt
    0b0111: "LDR",    # Load data from memory into a register
    0b1000: "STR",    # Store register data into memory
    0b1001: "CONST",  # Put a constant value into a register
    0b1111: "RET",    # Return/end the thread
}


class Decoder:
    def __init__(self):
        self.rd = 0
        self.rs = 0
        self.rt = 0
        self.nzp = 0
        self.immediate = 0

        self.write_to_register = False
        self.alu_op = None
        self.is_load = False
        self.is_store = False
        self.is_const = False
        self.is_branch = False
        self.is_compare = False
        self.is_ret = False

    def decode(self, instruction):

        self.rd = 0
        self.rs = 0
        self.rt = 0
        self.nzp = 0
        self.immediate = 0

        self.write_to_register = False
        self.alu_op = None
        self.is_load = False
        self.is_store = False
        self.is_const = False
        self.is_branch = False
        self.is_compare = False
        self.is_ret = False

        if instruction is None:
            return

        self.rd = (instruction >> 8) & 0xF
        self.rs = (instruction >> 4) & 0xF
        self.rt = instruction & 0xF
        self.nzp = (instruction >> 9) & 0x7
        self.immediate = instruction & 0xFF

        # Get the first 4 bits = opcode
        opcode = (instruction >> 12) & 0xF

        if opcode == 0b0000:
            # NOP: Do nothing
            pass

        elif opcode == 0b0001:
            # BRnzp:
            self.is_branch = True

        elif opcode == 0b0010:
            # CMP: Compare registers
            self.is_compare = True

        elif opcode == 0b0011:
            # ADD: rd = rs + rt
            self.write_to_register = True
            self.alu_op = "ADD"

        elif opcode == 0b0100:
            # SUB: rd = rs - rt
            self.write_to_register = True
            self.alu_op = "SUB"

        elif opcode == 0b0101:
            # MUL: rd = rs * rt
            self.write_to_register = True
            self.alu_op = "MUL"

        elif opcode == 0b0110:
            # DIV: rd = rs / rt
            self.write_to_register = True
            self.alu_op = "DIV"

        elif opcode == 0b0111:
            # LDR: rd = data from memory[rs]
            self.write_to_register = True
            self.is_load = True

        elif opcode == 0b1000:
            # STR: memory[rs] = rt
            self.is_store = True

        elif opcode == 0b1001:
            # CONST: rd = immediate value
            self.write_to_register = True
            self.is_const = True

        elif opcode == 0b1111:
            # RET: Return / finish this thread
            self.is_ret = True

    def get_branch_condition(self):
        cond = []
        if self.nzp & 4: # 111(nzp) & 100(4)
            cond.append('N')
        if self.nzp & 2:
            cond.append('Z')
        if self.nzp & 1:
            cond.append('P')
        return cond