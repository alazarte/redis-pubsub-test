import redis
import json

from config import Config

DEFAULT_CONFIG_FILEPATH='./config/config.json'
DEFAULT_CHANNEL_NAME='test'

# Class to communicate to Redis Service

class Redis():

    config = None
    queue = None
    channel = None
    redis_channel_name = None

    def __init__(self, config_filepath = None):

        self.config = Config()

        with open(config_filepath or DEFAULT_CONFIG_FILEPATH, 'r') as handler:
            self.config.__dict__ = json.load(handler)

        self.redis_channel_name = 'test'

        self.__init_queue()
        self.__init_channel()

    def __init_queue(self):

        self.queue = redis.StrictRedis(
            host=self.config.redis_host,
            port=self.config.redis_port,
            db=self.config.redis_db,
            decode_responses=True)

    def __init_channel(self):

        self.channel = self.queue.pubsub()
        self.channel.subscribe(self.redis_channel_name)

    # Username is only created at the beginning, so join to channel default
    def set_user(self, string):

        if not self.__check_key_exists(string):

            self.queue.hset('user-channel', string, DEFAULT_CHANNEL_NAME)

            return True

        return False

    def set_channel(self, username, channel_name):

        self.queue.hdel('user-channel', username)
        self.queue.hset('user-channel', username, channel_name)

        self.queue.lpush('channel-list', channel_name)

        self.channel.subscribe(channel_name)

    def __check_key_exists(self, string):

        all_keys = self.queue.hkeys('user-channel')

        for key in all_keys:

            print("{} {}".format(key, string))

            if key == string:

                return True

        return False

    def list_users(self):

        return self.queue.hkeys('user-channel')

    def list_channels(self):

        return self.queue.lrange('channel-list', 0, -1)
