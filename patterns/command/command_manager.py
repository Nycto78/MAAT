class CommandManager:
    def __init__(self):
        self.undo_stack = []
        self.redo_stack = []

    def execute_command(self, command):
        if command.execute():
            self.undo_stack.append(command)
            self.redo_stack.clear()

    def undo_last(self):
        if self.undo_stack:
            last_command = self.undo_stack.pop()
            if last_command.undo():
                self.redo_stack.append(last_command)

    def redo_last(self):
        if self.redo_stack:
            command = self.redo_stack.pop()
            if command.execute():
                self.undo_stack.append(command)
