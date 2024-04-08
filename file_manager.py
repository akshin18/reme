import json


class FileManager:
    def __init__(self):
        self.data = None
        self.data_index = 0

    def load_data(self):
        try:
            with open(f"data.json", "r") as f:
                self.data = json.loads(f.read())
                self.data_index = 0
        except FileNotFoundError:
            with open(f"data.json", "w") as f:
                f.write("{}")
            self.data = {}
        except:
            print("Something went wrong loading data.json")

    def save_data(self):
        with open(f"data.json", "w") as f:
            f.write(json.dumps(self.data))

    def push_data(self, session_name, user_name, host, port, pwd):
        if pwd.endswith(".key"):
            with open(pwd, "r") as f:
                pwd = f.read()
        self.data[session_name] = {
            "user": user_name,
            "host": host,
            "port": port,
            "pwd": pwd,
        }
        self.save_data()

    def delete_data(self, session_name):
        del self.data[session_name]
        self.save_data()
