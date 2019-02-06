from decorators import command
from decorators import available_commands

def command_for(string):
    return available_commands[string]

@command('list')
def list(self):
    print("List command")

@command('exit')
def list(self):
    print("Exit command")
