class MemoryController:
    def __init__(self, memory):
        self.memory = memory
        self.ready = 0
        self.data = None

    def read(self, address):
        if 0 <= address < len(self.memory):
            return self.memory[address]
        return 0

    def write(self, address, data):
        if 0 <= address < len(self.memory):
            self.memory[address] = data
