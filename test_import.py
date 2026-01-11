from filesystem import MockFileSystem
from command_parser import CommandParser
class StubUI:
    def __init__(self):
        self.filesystem = MockFileSystem()
        self.username = 'student'
        self.hostname = 'simulator'
        self.command_history = []
        self.session_log = []
        self.inline_input = True
        self.root = None
ui = StubUI()
cp = CommandParser(ui)
print('OK')
print('Has ln:', hasattr(cp, 'cmd_ln'))
print('Has locate:', hasattr(cp, 'cmd_locate'))
print('Has sort:', hasattr(cp, 'cmd_sort'))
print('Commands include ln?', 'ln' in cp.commands)
