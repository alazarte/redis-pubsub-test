import fileinput
import logging
import signal
import re
import time

from  redis_connection import Redis

MIN_CHAR_NAMES=4

class Chat():

    config = None
    logger = None
    message_help = None
    username = None

    def __init__(self):

        self.redis = Redis()

        original_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
        signal.signal(signal.SIGINT, original_sigint_handler)

        logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

        self.help_message = """
Available commands
    listen          Get all messages queued in redis
    exit            Exit app
    channel [name]  Change channel to [name]
    list            List all channels and all users connected
    [string]    Publish string to redis
        """

    def __check_name(self, prompt, allow_duplicate=True, tries=0):

        line = input(prompt).lower()

        if len(line) < MIN_CHAR_NAMES :
            self.logger.info("Invalid length, shoud be more than {}".format(MIN_CHAR_NAMES))
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

        message_exit = '^exit$'
        message_listen = '^listen$'
        message_channel = '^channel ([a-z]*)'
        message_list = '^list$'

        match_exit = re.compile(message_exit)
        match_listen = re.compile(message_listen)
        match_channel = re.compile(message_channel)
        match_list = re.compile(message_list)

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

            if match_exit.match(line):

                self.__quit_chat()
                break

            elif match_listen.match(line):
                self.logger.info("Hit CTRL+C to stop listening...")
                try:
                    while True:
                        message = self.redis.get_message()
                        if message:
                            self.logger.debug("%s" % (message))
                            if isinstance(message['data'],str) and ':' in message['data']:
                                user_from = message['data'].split(':')[0]
                                data = message['data'].split(':')[1:]
                            else:
                                user_from = "system"
                                data = message['data']
                            self.logger.info("#{}-{}: {}"
                                .format(message['channel'], user_from, data))
                        time.sleep(1)
                except KeyboardInterrupt:
                    self.logger.info("Stop listening")

            elif match_channel.match(line):
                m = match_channel.match(line)
                new_channel_name = m.group(1)
                self.logger.info("Change channel name to {}".format(new_channel_name))
                self.redis.set_channel(self.username, new_channel_name)
                # Check if channel exists, if not create a new one

            elif match_list.match(line):
                all_list = self.redis.get_channels()
                self.logger.info(all_list)

            else:
                self.logger.debug("Sending...")
                self.redis.publish("{}:{}".format(self.username, line))

chat = Chat()
chat.chat()

