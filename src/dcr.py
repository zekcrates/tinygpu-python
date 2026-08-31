# device control register 
# just stores thread count 

class DeviceControlRegister:
    def __init__(self):
        self.thread_count = 0

    def reset(self):
        self.thread_count = 0

    def set_thread_count(self, count):
        self.thread_count = count

    def get_thread_count(self):
        return self.thread_count