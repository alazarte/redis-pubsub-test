import redis
import json

from config import Config

DEFAULT_CONFIG_FILEPATH='./config/config.json'
DEFAULT_CHANNEL_NAME='test'

CHANNELS_LIST='channels-list'

# Class to communicate to Redis Service

class Redis():

    __config = None
    __queue = None
    __channel = None
    __channel_name = None

    def __init__(self, config_filepath = None):

        self.__config = Config()

        with open(config_filepath or DEFAULT_CONFIG_FILEPATH, 'r') as handler:
            self.__config.__dict__ = json.load(handler)

        self.__init_queue()
        self.__init_channel()

    def __init_queue(self):

        self.__queue = redis.StrictRedis(
            host=self.__config.redis_host,
            port=self.__config.redis_port,
            db=self.__config.redis_db,
            decode_responses=True)

    def __init_channel(self):

        self.__channel = self.__queue.pubsub()
        self.__channel.subscribe(DEFAULT_CHANNEL_NAME)
        self.__channel_name = DEFAULT_CHANNEL_NAME

    # Username is only created at the beginning, so join to channel default

    def set_channel(self, username, new_channel):

        print("Unsubscribing from {}".format(self.__channel_name))
        self.__channel.unsubscribe(self.__channel_name)

        self.__queue.lrem(CHANNELS_LIST, 0, new_channel)
        self.__queue.lpush(CHANNELS_LIST, new_channel)

        self.__channel_name = new_channel

        print("Subscribing to {}".format(self.__channel_name))
        self.__channel.subscribe(self.__channel_name)

        self.__queue.sadd(self.__channel_name, username)

    def __check_all_members(self, string):

        all_members = self.get_users()

        for value in all_members:

            if string == value:

                return True

        return False

    def __get_all_members_from_set(self):

        response = {}
        all_keys = self.__queue.lrange(CHANNELS_LIST, 0, -1)

        for key in all_keys:

            response[key] = list(self.__queue.smembers(key))

        return response

    def get_users(self):

        response = []

        members = self.__get_all_members_from_set()

        for key in members:

            response.extend(members[key])

        return response

    def get_channels(self):

        return self.__get_all_members_from_set()

    def get_users_current_channel(self):

        return self.__queue.smembers(self.__channel_name)

    def remove_user(self, username):

        self.__queue.srem(self.__channel_name, username)

    def check_duplicate(self, string):

        return self.__check_all_members(string)

    def publish(self, message):

        self.__queue.publish(self.__channel_name, message)

    def get_message(self):

        return self.__channel.get_message()
