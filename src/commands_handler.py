import re

from command import Command

class CommandsHandler():

    __commands = None

    def __init__(self):

        self.__commands = []

    def add_command(self, command_name, match_string, method_action, help_message, contains_arguments=False):

        command = Command()

        command.name = command_name
        command.action = method_action
        command.match = re.compile(match_string)
        command.help = help_message
        command.contains_arguments = contains_arguments

        self.__commands.append(command)

    def parse_command(self, string):

        for command in self.__commands:

            if command.match.match(string):

                if command.contains_arguments:

                    return command.action, command.match.match(string)

                return command.action, None

    def get_help_message(self):

        help_message = ""

        for command in self.__commands:

            help_message += "\t{}: {}\n".format(command.name, command.help)

        return help_message
