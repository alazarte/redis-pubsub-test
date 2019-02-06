available_commands = None

def command(command_name):

    def wrapper(command_method):

        def wrapped():

            command_method()

            avaiable_commands[command_name] = command_method

        return wrapped

    return wrapper
