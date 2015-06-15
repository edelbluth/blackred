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
__version__ = '0.2.0'


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

    def __init__(self,
                 redis_host: str=None,
                 redis_port: int=None,
                 redis_db: int=None,
                 redis_use_socket: bool=None):
        """
        Create an Instance of BlackRed with configuration for Redis connection

        :param str redis_host: Hostname, IP Address or Socket
        :param int redis_port: Port Number
        :param int redis_db: DB Number
        :param bool redis_use_socket: True, when a socket should be used instead the TCP/IP connection
        """
        if redis_host is None:
            redis_host = BlackRed.Settings.REDIS_HOST
        if redis_port is None:
            redis_port = BlackRed.Settings.REDIS_PORT
        if redis_db is None:
            redis_db = BlackRed.Settings.REDIS_DB
        if redis_use_socket is None:
            redis_use_socket = BlackRed.Settings.REDIS_USE_SOCKET

        self.__selected_db = redis_db

        if redis_use_socket:
            self.__connection_pool = redis.ConnectionPool(
                connection_class=UnixDomainSocketConnection,
                path=redis_host,
                db=redis_db,
            )
        else:
            self.__connection_pool = redis.ConnectionPool(
                host=redis_host,
                port=redis_port,
                db=redis_db,
            )

    def __get_connection(self) -> redis.Redis:
        """
        Get a Redis connection from the connection pool

        :return: Redis connection instance
        :rtype: redis.Redis
        """
        return redis.Redis(connection_pool=self.__connection_pool, db=self.__selected_db)

    def _encode_item(self, item: str) -> str:
        """
        If anonymization is on, an item gets salted and hashed here.

        :param str item:
        :return: Hashed item, if anonymization is on; the unmodified item otherwise
        :rtype: str
        """
        assert item is not None
        if not BlackRed.Settings.ANONYMIZATION:
            return item
        connection = self.__get_connection()
        salt = connection.get(BlackRed.Settings.SALT_KEY)
        if salt is None:
            salt = create_salt()
            connection.set(BlackRed.Settings.SALT_KEY, salt)
        return sha512(salt + item.encode()).hexdigest()

    def __get_ttl(self, item: str) -> int:
        """
        Get the amount of time a specific item will remain in the database.

        :param str item: The item to get the TTL for
        :return: Time in seconds. Returns None for a non-existing element.
        :rtype: int
        """
        connection = self.__get_connection()
        return connection.ttl(item)

    def get_blacklist_ttl(self, item: str) -> int:
        """
        Get the amount of time a specific item will remain on the blacklist.

        :param str item: The item to get the TTL for on the blacklist
        :return: Time in seconds. Returns None for a non-existing element.
        :rtype: int
        """
        assert item is not None
        item = self._encode_item(item)
        return self.__get_ttl(BlackRed.Settings.BLACKLIST_KEY_TEMPLATE.format(item))

    def get_watchlist_ttl(self, item: str) -> int:
        """
        Get the amount of time a specific item will remain on the watchlist.

        :param str item: The item to get the TTL for on the watchlist
        :return: Time in seconds. Returns None for a non-existing element
        :rtype: int
        """
        assert item is not None
        item = self._encode_item(item)
        return self.__get_ttl(BlackRed.Settings.WATCHLIST_KEY_TEMPLATE.format(item))

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
        key = BlackRed.Settings.BLACKLIST_KEY_TEMPLATE.format(item)
        value = connection.get(key)
        if value is None:
            # self.__connection_pool.release(connection)
            return True
        if BlackRed.Settings.BLACKLIST_REFRESH_TTL_ON_HIT:
            connection.expire(key, BlackRed.Settings.BLACKLIST_TTL_SECONDS)
        # self.__connection_pool.release(connection)
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
        if not self.is_not_blocked(item):
            return
        connection = self.__get_connection()
        key = BlackRed.Settings.WATCHLIST_KEY_TEMPLATE.format(item)
        value = connection.get(key)
        if value is None:
            connection.set(key, 1, ex=BlackRed.Settings.WATCHLIST_TTL_SECONDS)
            # self.__connection_pool.release(connection)
            return
        value = int(value) + 1
        if value < BlackRed.Settings.WATCHLIST_TO_BLACKLIST_THRESHOLD:
            connection.set(key, value, ex=BlackRed.Settings.WATCHLIST_TTL_SECONDS)
            # self.__connection_pool.release(connection)
            return
        blacklist_key = BlackRed.Settings.BLACKLIST_KEY_TEMPLATE.format(item)
        connection.set(blacklist_key, time.time(), ex=BlackRed.Settings.BLACKLIST_TTL_SECONDS)
        connection.delete(key)
        # self.__connection_pool.release(connection)

    def unblock(self, item: str) -> None:
        """
        Unblock an item and/or reset it's fail count

        :param str item: The item to unblock
        """
        assert item is not None
        item = self._encode_item(item)
        watchlist_key = BlackRed.Settings.WATCHLIST_KEY_TEMPLATE.format(item)
        blacklist_key = BlackRed.Settings.BLACKLIST_KEY_TEMPLATE.format(item)
        connection = self.__get_connection()
        connection.delete(watchlist_key)
        connection.delete(blacklist_key)
        # self.__connection_pool.release(connection)
