import redis
import fileinput
import logging
import signal

class Config(object):

    redis_host  = None
    redis_port  = None
    redis_db    = None

    redis_channel_name = None

class Chat():

    config = None
    logger = None
    message_help = None
    queue = None
    channel = None

    def __init__(self):

        self.config = Config()

        self.config.redis_host = 'redis-service'
        self.config.redis_port = 6379
        self.config.redis_db = 0

        self.config.redis_channel_name = 'test'

        original_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
        signal.signal(signal.SIGINT, original_sigint_handler)

        logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

        self.help_message = """
Available commands
    listen      Get all messages queued in redis
    exit        Exit app
    [string]    Publish string to redis
        """

        self.__init_channel()
        self.__init_queue()

    def __init_channel(self):
        self.queue = redis.StrictRedis(
            host=self.config.redis_host,
            port=self.config.redis_port,
            db=self.config.redis_db)

    def __init_queue(self):

        self.channel = self.queue.pubsub()
        self.channel.subscribe(self.config.redis_channel_name)

    def chat(self):

        self.logger.info(self.help_message)

        while True:

            try:
                line = input("> ")
            except KeyboardInterrupt:
                self.logger.info("Bye...")
                break

            if '' == line:
                continue

            self.logger.debug("Processing '%s'" % line)

            if 'exit' in line:
                self.logger.info("Bye...")
                break

            elif 'listen' in line:
                self.logger.debug("Listening...")
                message = self.channel.get_message()
                while message:
                    self.logger.info("%s: %s" % (self.config.redis_channel_name, message))
                    message = self.channel.get_message()
                self.logger.info("End of message queue")

            else:
                self.logger.debug("Sending...")
                self.queue.publish(self.config.redis_channel_name, line)

chat = Chat()
chat.chat()

