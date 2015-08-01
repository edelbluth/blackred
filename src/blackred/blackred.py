"""
Copyright 2015 Juergen Edelbluth

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


__author__ = 'Juergen Edelbluth'
__version__ = '0.3.0'


import redis
from redis.connection import UnixDomainSocketConnection
import time
from hashlib import sha512
from random import SystemRandom


def create_salt(length: int=128) -> bytes:
    """
    Create a new salt

    :param int length: How many bytes should the salt be long?
    :return: The salt
    :rtype: bytes
    """
    return b''.join(bytes([SystemRandom().randint(0, 255)]) for _ in range(length))


class BlackRed(object):

    class Settings:

        WATCHLIST_KEY_TEMPLATE = 'BlackRed:WatchList:{:s}'
        BLACKLIST_KEY_TEMPLATE = 'BlackRed:BlackList:{:s}'
        SALT_KEY = 'BlackRed:AnonymizationListSecret'
        WATCHLIST_TTL_SECONDS = 180
        BLACKLIST_TTL_SECONDS = 86400
        WATCHLIST_TO_BLACKLIST_THRESHOLD = 3
        BLACKLIST_REFRESH_TTL_ON_HIT = True

        ANONYMIZATION = False

        REDIS_HOST = 'localhost'
        REDIS_PORT = 6379
        REDIS_DB = 0
        REDIS_USE_SOCKET = False
        REDIS_AUTH = None

    def __init__(self,
                 redis_host: str=None,
                 redis_port: int=None,
                 redis_db: int=None,
                 redis_use_socket: bool=None,
                 redis_auth: str=None):
        """
        Create an Instance of BlackRed with configuration for Redis connection

        :param str redis_host: Hostname, IP Address or Socket
        :param int redis_port: Port Number
        :param int redis_db: DB Number
        :param bool redis_use_socket: True, when a socket should be used instead the TCP/IP connection
        :param str redis_auth: If set, the redis AUTH command will be used with the given password
        """
        if redis_host is None:
            redis_host = BlackRed.Settings.REDIS_HOST
        if redis_port is None:
            redis_port = BlackRed.Settings.REDIS_PORT
        if redis_db is None:
            redis_db = BlackRed.Settings.REDIS_DB
        if redis_use_socket is None:
            redis_use_socket = BlackRed.Settings.REDIS_USE_SOCKET
        if redis_auth is None:
            redis_auth = BlackRed.Settings.REDIS_AUTH

        self.__selected_db = redis_db
        self.__redis_host = redis_host
        self.__redis_port = redis_port
        self.__redis_db = redis_db
        self.__redis_use_socket = redis_use_socket
        self.__redis_auth = redis_auth

        self.__redis_conf = {
            'watchlist_template': BlackRed.Settings.WATCHLIST_KEY_TEMPLATE,
            'blacklist_template': BlackRed.Settings.BLACKLIST_KEY_TEMPLATE,
            'salt_key': BlackRed.Settings.SALT_KEY,
            'watchlist_ttl': BlackRed.Settings.WATCHLIST_TTL_SECONDS,
            'blacklist_ttl': BlackRed.Settings.BLACKLIST_TTL_SECONDS,
            'watchlist_to_blacklist': BlackRed.Settings.WATCHLIST_TO_BLACKLIST_THRESHOLD,
            'blacklist_refresh_ttl': BlackRed.Settings.BLACKLIST_REFRESH_TTL_ON_HIT,
            'anonymization': BlackRed.Settings.ANONYMIZATION,
        }

    def __get_connection(self) -> redis.Redis:
        """
        Get a Redis connection

        :return: Redis connection instance
        :rtype: redis.Redis
        """

        if self.__redis_use_socket:
            r = redis.from_url(
                'unix://{:s}?db={:d}'.format(
                    self.__redis_host,
                    self.__redis_db
                )
            )
        else:
            r = redis.from_url(
                'redis://{:s}:{:d}/{:d}'.format(
                    self.__redis_host,
                    self.__redis_port,
                    self.__redis_db
                )
            )

        if BlackRed.Settings.REDIS_AUTH is not None:
            r.execute_command('AUTH {:s}'.format(BlackRed.Settings.REDIS_AUTH))
        return r

    def __release_connection(self, connection: redis.Redis) -> None:
        """
        Close a Redis connection explicitly

        :param redis.Redis connection: Connection to be closed
        """
        del connection

    def _encode_item(self, item: str) -> str:
        """
        If anonymization is on, an item gets salted and hashed here.

        :param str item:
        :return: Hashed item, if anonymization is on; the unmodified item otherwise
        :rtype: str
        """
        assert item is not None
        if not self.__redis_conf['anonymization']:
            return item
        connection = self.__get_connection()
        salt = connection.get(self.__redis_conf['salt_key'])
        if salt is None:
            salt = create_salt()
            connection.set(self.__redis_conf['salt_key'], salt)
        self.__release_connection(connection)
        return sha512(salt + item.encode()).hexdigest()

    def __get_ttl(self, item: str) -> int:
        """
        Get the amount of time a specific item will remain in the database.

        :param str item: The item to get the TTL for
        :return: Time in seconds. Returns None for a non-existing element.
        :rtype: int
        """
        connection = self.__get_connection()
        ttl = connection.ttl(item)
        self.__release_connection(connection)
        return ttl

    def get_blacklist_ttl(self, item: str) -> int:
        """
        Get the amount of time a specific item will remain on the blacklist.

        :param str item: The item to get the TTL for on the blacklist
        :return: Time in seconds. Returns None for a non-existing element.
        :rtype: int
        """
        assert item is not None
        item = self._encode_item(item)
        return self.__get_ttl(self.__redis_conf['blacklist_template'].format(item))

    def get_watchlist_ttl(self, item: str) -> int:
        """
        Get the amount of time a specific item will remain on the watchlist.

        :param str item: The item to get the TTL for on the watchlist
        :return: Time in seconds. Returns None for a non-existing element
        :rtype: int
        """
        assert item is not None
        item = self._encode_item(item)
        return self.__get_ttl(self.__redis_conf['watchlist_template'].format(item))

    def is_not_blocked(self, item: str) -> bool:
        """
        Check if an item is _not_ already on the blacklist

        :param str item: The item to check
        :return: True, when the item is _not_ on the blacklist
        :rtype: bool
        """
        assert item is not None
        item = self._encode_item(item)
        connection = self.__get_connection()
        key = self.__redis_conf['blacklist_template'].format(item)
        value = connection.get(key)
        if value is None:
            self.__release_connection(connection)
            return True
        if self.__redis_conf['blacklist_refresh_ttl']:
            connection.expire(key, self.__redis_conf['blacklist_ttl'])
        self.__release_connection(connection)
        return False

    def is_blocked(self, item: str) -> bool:
        """
        Check if an item is on the blacklist

        :param str item: The item to check
        :return: True, when the item is on the blacklist
        :rtype: bool
        """
        return not self.is_not_blocked(item)

    def log_fail(self, item: str) -> None:
        """
        Log a failed action for an item. If the fail count for this item reaches the threshold, the item is moved to the
        blacklist.

        :param str item: The item to log
        """
        assert item is not None
        item = self._encode_item(item)
        if self.is_blocked(item):
            return
        connection = self.__get_connection()
        key = self.__redis_conf['watchlist_template'].format(item)
        value = connection.get(key)
        if value is None:
            connection.set(key, 1, ex=self.__redis_conf['watchlist_ttl'])
            self.__release_connection(connection)
            return
        value = int(value) + 1
        if value < self.__redis_conf['watchlist_to_blacklist']:
            connection.set(key, value, ex=self.__redis_conf['watchlist_ttl'])
            self.__release_connection(connection)
            return
        blacklist_key = self.__redis_conf['blacklist_template'].format(item)
        connection.set(blacklist_key, time.time(), ex=self.__redis_conf['blacklist_ttl'])
        connection.delete(key)
        self.__release_connection(connection)

    def unblock(self, item: str) -> None:
        """
        Unblock an item and/or reset it's fail count

        :param str item: The item to unblock
        """
        assert item is not None
        item = self._encode_item(item)
        watchlist_key = self.__redis_conf['watchlist_template'].format(item)
        blacklist_key = self.__redis_conf['blacklist_template'].format(item)
        connection = self.__get_connection()
        connection.delete(watchlist_key)
        connection.delete(blacklist_key)
        self.__release_connection(connection)
