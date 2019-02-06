import fileinput
import logging
import signal
import re
import time

from  redis_connection import Redis

MIN_CHAR_NAMES=8

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

        line = input("username > ").lower()

        if not self.redis.set_user(line):
            self.logger.info("Username already exists...")
            return
        elif not len(line) < MIN_CHAR_NAMES:
            self.logger.info("Name length should be more than {}".format(MIN_CHAR_NAMES))

        self.username = line

        line = input("channel > ").lower()

        if self.redis.set_channel(self.username, line):
            self.logger.info("New channel")
        elif not len(line) < MIN_CHAR_NAMES:
            self.logger.info("Name length should be more than {}".format(MIN_CHAR_NAMES))
        else:
            self.logger.info("Joining channel")

        while True:

            try:

                line = input("> ").lower()

            except KeyboardInterrupt:

                self.logger.info("Bye...")
                break

            if '' == line:
                continue

            if match_exit.match(line):
                self.logger.info("Bye...")
                break

            elif match_listen.match(line):
                self.logger.info("Hit CTRL+C to stop listening...")
                try:
                    while True:
                        message = self.redis.channel.get_message()
                        if message:
                            self.logger.info("%s: %s" % (self.redis.redis_channel_name, message))
                        time.sleep(1)
                except KeyboardInterrupt:
                    self.logger.info("Stop listening")

            elif match_channel.match(line):
                m = match_channel.match(line)
                channel_name = m.group(1)
                self.logger.info("Change channel name to {}".format(channel_name))
                self.redis.set_channel(channel_name)
                # Check if channel exists, if not create a new one

            elif match_list.match(line):
                match_list.match(line)
                all_list = self.redis.list_users()
                self.logger.info(all_list)
                all_list = self.redis.list_channels()
                self.logger.info(all_list)

            else:
                self.logger.debug("Sending...")
                self.redis.queue.publish(self.redis.redis_channel_name, line)

chat = Chat()
chat.chat()

