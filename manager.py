



class Manager:
    def __init__(self):
        self.state = 0
        self.button_state = 0
        self.edit_session = ""
        self.edit_session_index = 0
        self.commands = ["mk", "qw", "im"]

    def check_command(self):
        for command in self.commands:
            if self.buffer.endswith(command):
                self.__getattribute__(command)()