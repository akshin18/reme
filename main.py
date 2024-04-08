import os

import curses
from curses import wrapper

from file_manager import FileManager
from buffer import Buffer


class Terminal(FileManager, Buffer):
    def __init__(self, stdscr: curses.window) -> None:
        self.stdscr = stdscr
        FileManager.__init__(self)
        Buffer.__init__(self)

    def init_styles(self):
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)

    def main_settings(self):
        curses.start_color()
        curses.use_default_colors()
        curses.curs_set(0)
        self.stdscr.attron(curses.A_BOLD)

    def menu(self):
        self.stdscr.clear()

        for zi, session_name in enumerate(self.data):
            if zi == self.data_index:
                self.stdscr.addstr(zi, 0, session_name, curses.color_pair(1))
            else:
                self.stdscr.addstr(zi, 0, session_name)
        self.stdscr.refresh()

    def delete(self):
        self.menu()
        if self.button_state >= 0:
            if self.button_state == 0:
                self.stdscr.addstr(10, 15, "No", curses.color_pair(1))
                self.stdscr.addstr(10, 20, "Delete")
            else:
                self.stdscr.addstr(10, 15, "No")
                self.stdscr.addstr(10, 20, "Delete", curses.color_pair(1))
        else:
            self.button_state = 0
            self.state = 0

    def edit(self, edit=False):
        self.stdscr.clear()
        self.stdscr.addstr(0, 0, "Edit Session:")
        self.session_info = [
            f"Session Name: {self.edit_session}",
            f"Username: {self.data[self.edit_session].get('user')}",
            f"Host: {self.data[self.edit_session].get('host')}",
            f"Port: {self.data[self.edit_session].get('port')}",
            f"Password: {self.data[self.edit_session].get('pwd') if not self.data[self.edit_session].get('pwd').startswith('-----BEGIN RSA PRIVATE KEY-----') else 'Private Key ...'}"
        ]

        for zi, i in enumerate(self.session_info):
            if zi == self.edit_session_index:
                self.stdscr.addstr(2 + zi, 0, i, curses.color_pair(1))
            else:
                self.stdscr.addstr(2 + zi, 0, i)

        self.stdscr.refresh()
        if edit == True:
            curses.curs_set(1)
            info = self._listen(cursor_y=15)
            curses.curs_set(0)
            self.state = 2
            if info != None:
                if self.edit_session_index == 0:
                    self.data[info] = self.data[self.edit_session]
                    del self.data[self.edit_session]
                    self.edit_session = info
                elif self.edit_session_index == 1:
                    self.data[self.edit_session]["username"] = info
                elif self.edit_session_index == 2:
                    self.data[self.edit_session]["host"] = info
                elif self.edit_session_index == 3:
                    self.data[self.edit_session]["port"] = info
                elif self.edit_session_index == 4:
                    if info.endswith(".key"):
                        with open(info,"r")as f:
                            info = f.read()
                    self.data[self.edit_session]["pwd"] = info
                self.save_data()
            return self.edit()

    def monitor(self):
        self.menu()
        while True:
            key = self.stdscr.getch()
            if key == curses.KEY_UP:
                if self.state == 0 and self.data_index > 0:
                    self.data_index -= 1
                    self.menu()
                elif self.state == 2 and self.edit_session_index > 0:
                    self.edit_session_index -= 1
                    self.edit()
            elif key == curses.KEY_DOWN:
                if self.state == 0 and self.data_index < len(self.data)-1:
                    self.data_index += 1
                    self.menu()
                elif self.state == 2 and self.edit_session_index < len(self.session_info)-1:
                    self.edit_session_index += 1
                    self.edit()
            elif key == ord("\n") or key == curses.KEY_ENTER:
                if self.state == 0:
                    session = self.data[list(self.data.keys())[self.data_index]]
                    user = session["user"]
                    pwd = session["pwd"]
                    host = session["host"]
                    port = session["port"]
                    if pwd.startswith("-----BEGIN RSA PRIVATE KEY-----"):
                        with open("asd.key", "w")as f:
                            f.write(pwd)
                        os.system("chmod 600 asd.key")
                        return f"ssh -p {port} -i asd.key {user}@{host}"
                    return f"sshpass -p {pwd} ssh -p {port} {user}@{host}"
                elif self.state == 2:
                    self.state = 3
                    self.edit(edit=True)
                elif self.state == 1:
                    if self.button_state == 1:
                        self.delete_data(list(self.data.keys())[self.data_index])
                    self.state = 0
                    self.button_state = 0
                    self.data_index = 0
                    self.menu()

            elif key == 260 or key == curses.KEY_LEFT:
                if self.state == 0:
                    self.state = 1
                    self.delete()
                elif self.state == 1:
                    self.button_state -= 1
                    self.delete()
                elif self.state == 2:
                    self.edit_session_index = 0
                    self.state = 0
                    self.menu()
            elif key == 261 or key == curses.KEY_RIGHT:
                if self.state == 0:
                    self.edit_session = list(self.data.keys())[self.data_index]
                    self.state = 2
                    self.edit()
                elif self.state == 1:
                    if self.button_state == 0:
                        self.button_state = 1
                        self.delete()
                elif self.state == 2:
                    self.state = 3
                    self.edit(edit=True)
            else:
                self.check_buffer(chr(key))

    def _listen(self, text=None, cursor_y = 2):
        if text != None:
            self.stdscr.clear()
            self.stdscr.addstr(text)

        input_string = ""
        cursor_x = 0
        self.stdscr.move(cursor_y, cursor_x)
        self.stdscr.refresh()

        while True:
            key = self.stdscr.getch()
            if key != curses.ERR:
                if key == curses.KEY_BACKSPACE or key == 127:
                    if cursor_x > 0:
                        input_string = input_string[:cursor_x - 1] + input_string[cursor_x:]
                        cursor_x -= 1
                        self.stdscr.move(cursor_y, cursor_x)
                        self.stdscr.clrtoeol()
                        self.stdscr.refresh()
                elif key == curses.KEY_LEFT:
                    if cursor_x > 0:
                        cursor_x -= 1
                elif key == curses.KEY_RIGHT:
                    if cursor_x < len(input_string):
                        cursor_x += 1
                elif key == ord("\n"):
                    return input_string
                elif key == 4 or key == 17:
                    return None
                else:
                    input_string = input_string[:cursor_x] + chr(key) + input_string[cursor_x:]
                    cursor_x += 1

                if text != None:
                    self.stdscr.clear()
                    self.stdscr.addstr(text)
                self.stdscr.addstr(cursor_y,0,input_string)
                self.stdscr.refresh()
                
                self.stdscr.move(cursor_y, cursor_x )

            self.stdscr.refresh()


    
    def mk(self):
        curses.curs_set(1)

        session_name = self._listen("Session name: ")
        if session_name == None:
            curses.curs_set(0)
            self.menu()
            return
        creds = self._listen("Credentials (user:host:port or user:host): ")
        if creds == None:
            curses.curs_set(0)
            self.menu()
            return
        creds_list = creds.strip().split(":")
        username = creds_list[0].strip()
        host = creds_list[1].strip()
        if len(creds_list) == 3:
            port = creds_list[2].strip()
        else:
            port = "22"
        
        pwd = self._listen("Password: ")
        if pwd == None:
            curses.curs_set(0)
            self.menu()
            return
        pwd = pwd.strip()
        self.push_data(session_name, username, host, port, pwd)

        curses.curs_set(0)
        self.menu()
    
    def qw(self):
        raise KeyboardInterrupt
    
    def im(self):
        curses.curs_set(1)
        file = self._listen(text="Add file path: ")
        curses.curs_set(0)
        with open(file) as f:
            read_file = f.read()
        with open("data.json","w")as f:
            f.write(read_file)
        self.load_data()
        self.menu()

        


def main(stdscr: curses.window) -> None:
    terminal = Terminal(stdscr)
    terminal.load_data()
    terminal.init_styles()
    terminal.main_settings()
    return terminal.monitor()

if __name__ == '__main__':
    try:
        result = wrapper(main)
        if result != None:
            os.system(result)
    except KeyboardInterrupt:
        print("Bye...")
