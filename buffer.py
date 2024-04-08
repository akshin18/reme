from manager import Manager


class Buffer(Manager):
    def __init__(self):
        self.buffer = ""
        Manager.__init__(self)

    def check_buffer(self, key):
        self.buffer += key
        if len(self.buffer) >= 30:
            self.buffer = self.buffer[1:]

        self.check_command()
