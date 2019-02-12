import logging
import signal
import re
import time
import json

from  redis_connection import Redis
from config import Config
from commands_handler import CommandsHandler

MIN_CHAR_NAMES = 4
DEFAULT_CONFIG_FILEPATH = './config/config.json'
NAME_VALIDATE_REGEX = '^[a-zA-Z][a-zA-Z0-9]*$'

class Chat():

    __config = None
    logger = None
    message_help = None
    username = None

    def __init__(self, config_filepath=None):

        self.__config = Config()

        with open(config_filepath or DEFAULT_CONFIG_FILEPATH, 'r') as handler:
            self.__config.__dict__ = json.load(handler)

        self.redis = Redis(self.__config)

        original_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
        signal.signal(signal.SIGINT, original_sigint_handler)

        logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(self.__config.log_level)

        self.help_message = """
Available commands
    /listen          Get all messages queued in redis
    /exit            Exit app
    /channel [name]  Change channel to [name]
    /list            List all channels and all users connected
    /help            Display this help message
    [string]    Publish string to redis
        """

    def __check_name(self, prompt, allow_duplicate=True, tries=0):

        line = input(prompt).lower()

        if len(line) < MIN_CHAR_NAMES:
            self.logger.info("Invalid length, shoud be more than {}".format(MIN_CHAR_NAMES))
            tries += 1
            line = self.__check_name(prompt, allow_duplicate, tries)

        name_validator = re.compile(NAME_VALIDATE_REGEX)

        if not name_validator.match(line):
            self.logger.error("Name shoud be in the following format {}".format(NAME_VALIDATE_REGEX))
            tries += 1
            line = self.__check_name(prompt, allow_duplicate, tries)

        tries = 0

        if not allow_duplicate and self.redis.check_duplicate(line):

            self.logger.info("Found duplicate for {}".format(line))
            tries += 1
            line = self.__check_name(prompt, allow_duplicate, tries)

        return line

    def __quit_chat(self):

        self.redis.remove_user(self.username)
        self.logger.info("Bye...")

    def chat(self):

        command_handler = CommandsHandler()

        command_handler.add_command('^/exit$', self.command_exit, 'Exit chat')
        command_handler.add_command('^/listen$', self.command_listen, 'Get all messages queued in redis')
        command_handler.add_command('^/channel ([a-z]*)$', self.command_channel, 'Change channel to [name]', True)
        command_handler.add_command('^/list$', self.command_list, 'List all channel and users connected to them')
        command_handler.add_command('^/help$', self.command_help, 'Display this help message')
        command_handler.add_command('^(?!/)(.*)', self.command_send, 'Send message', True)

        self.logger.info(self.help_message)

        self.logger.info("Listing all users:")

        self.logger.info(self.redis.get_users())

        self.username = self.__check_name("username > ", False)

        self.logger.info("Listing all channels:")

        self.logger.info(self.redis.get_channels())

        channel_name = self.__check_name("channel > ")

        if self.redis.set_channel(self.username, channel_name):
            self.logger.info("Joining channel")

        self.logger.info("Listing users in channel:")

        self.logger.info(self.redis.get_users_current_channel())

        while True:

            try:

                line = input("> ").lower()

            except KeyboardInterrupt:

                self.__quit_chat()
                break

            if '' == line:
                continue

            try:
                action, arguments = command_handler.parse_command(line)
            except TypeError:
                self.logger.error("Command not found {}".format(line))
                continue

            if arguments:

                exit = action(arguments)

            else:

                exit = action()

            if exit:

                break

    def command_channel(self, args):

        new_channel_name = args.group(1)
        self.logger.info("Change channel name to {}".format(new_channel_name))
        self.redis.set_channel(self.username, new_channel_name)
        # Check if channel exists, if not create a new one

    def command_list(self):

        all_list = self.redis.get_channels()
        self.logger.info(all_list)

    def command_help(self):

        self.logger.info(self.help_message)

    def command_listen(self):

        self.logger.info("Hit CTRL+C to stop listening...")
        try:
            while True:
                message = self.redis.get_message()
                if message:
                    self.logger.debug("{}".format(message))
                    if isinstance(message['data'], str) and ':' in message['data']:
                        user_from = message['data'].split(':')[0]
                        data = "".join(message['data'].split(':')[1:])
                    else:
                        user_from = "system"
                        data = message['data']

                    self.logger.debug(message['data'])

                    self.logger.info("#{}-{}: {}"
                        .format(message['channel'], user_from, data))

                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Stop listening")

    def command_exit(self):

        self.__quit_chat()
        return True

    def command_send(self, args):

        m = args.group(1)

        self.logger.debug("Sending...")
        self.redis.publish("{}:{}".format(self.username, m))

