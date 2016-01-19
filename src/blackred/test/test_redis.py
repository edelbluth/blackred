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


import unittest
from time import sleep

from redis import Redis
from redis.exceptions import ResponseError

__author__ = 'Juergen Edelbluth'


class RedisTestBase(unittest.TestCase):

    redis = None
    """:type: Redis"""

    @classmethod
    def setUpClass(cls):
        cls.redis = Redis(host='localhost', port=6379, db=0)


class RedisLibraryNoAuthTest(RedisTestBase):

    redis = None
    """:type: Redis"""

    @classmethod
    def reset(cls):
        cls.redis.delete('test_set_str')
        cls.redis.delete('test_set_int')
        cls.redis.delete('this_should_not_exist')
        cls.redis.delete('test_to_be_expired')
        cls.redis.delete('test_umlauts')
        cls.redis.delete('test_byte')
        cls.redis.delete('test_delete')
        cls.redis.delete('test_this_one_is_not_there')
        cls.redis.delete('test_ttl')
        cls.redis.delete('test_some_invalid_key_ttl')

    @classmethod
    def setUpClass(cls):
        super(RedisLibraryNoAuthTest, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.reset()
        super(RedisLibraryNoAuthTest, cls).tearDownClass()

    def test_set_str(self):
        self.redis.set('test_set_str', 'test_set_value')
        value = self.redis.get('test_set_str')
        self.assertEqual(value, b'test_set_value')

    def test_set_int(self):
        self.redis.set('test_set_int', 101)
        value = self.redis.get('test_set_int')
        self.assertEqual(value, b'101')

    def test_non_existing_key(self):
        value = self.redis.get('this_should_not_exist')
        self.assertIsNone(value)

    def test_expiring(self):
        key = 'test_to_be_expired'
        self.redis.set(key, 'expire_value', ex=3)
        value = self.redis.get(key)
        self.assertEqual(value, b'expire_value')
        sleep(1)
        value = self.redis.get(key)
        self.assertEqual(value, b'expire_value')
        sleep(1)
        value = self.redis.get(key)
        self.assertEqual(value, b'expire_value')
        sleep(3)
        value = self.redis.get(key)
        self.assertIsNone(value)

    def test_umlauts(self):
        data = 'до́брый ве́чер! Grüß Gott! Nǐhǎo! 你好!'
        self.redis.set('test_umlauts', data)
        value = self.redis.get('test_umlauts')
        self.assertEqual(value, data.encode('utf-8'))

    def test_byte(self):
        data = b'\x62\x21\xaf\x99\x38\x82\xaf\xcc\xda\xef\xff\x00\x98\x99\xa3\x2a'
        self.redis.set('test_byte', data)
        value = self.redis.get('test_byte')
        self.assertEqual(value, data)

    def test_ttl(self):
        self.redis.set('test_ttl', 'test', ex=10)
        sleep(6)
        value = self.redis.ttl('test_ttl')
        self.assertIsNotNone(value)
        self.assertIsInstance(value, int)
        self.assertLess(value, 5)
        self.assertGreater(value, 3)
        self.redis.set('test_ttl', 'test', ex=10)
        sleep(1)
        value = self.redis.ttl('test_ttl')
        self.assertIsNotNone(value)
        self.assertIsInstance(value, int)
        self.assertGreater(value, 8)
        self.assertLess(value, 10)

    def test_expire(self):
        self.redis.set('test_expire', 'test_data', ex=5)
        sleep(3)
        self.redis.expire('test_expire', 10)
        sleep(2)
        value = self.redis.ttl('test_expire')
        self.assertGreater(value, 7)

    def test_delete(self):
        self.redis.set('test_delete', 'test_data')
        value = self.redis.get('test_delete')
        self.assertEqual(value, b'test_data')
        self.redis.delete('test_delete')
        value = self.redis.get('test_delete')
        self.assertIsNone(value)

    def test_delete_nonexistent(self):
        self.redis.delete('test_this_one_is_not_there')

    def test_ttl_for_invalid(self):
        value = self.redis.ttl('test_some_invalid_key_ttl')
        self.assertIsNone(value)

    def test_auth(self):
        self.assertRaises(ResponseError, self.redis.execute_command, 'AUTH x')


class RedisLibraryAuthTest(RedisLibraryNoAuthTest):

    @classmethod
    def setUpClass(cls):
        super(RedisLibraryAuthTest, cls).setUpClass()
        cls.redis.config_set('REQUIREPASS', 'password')
        cls.redis = Redis(host='localhost', port=6379, db=0)

    @classmethod
    def tearDownClass(cls):
        cls.redis.config_set('REQUIREPASS', '')
        cls.redis = Redis(host='localhost', port=6379, db=0)
        super(RedisLibraryAuthTest, cls).tearDownClass()

    def test_auth(self):
        self.assertRaises(ResponseError, self.redis.execute_command, 'AUTH x')
        self.redis.execute_command('AUTH password')


class RedisLibraryAuthFailTest(RedisTestBase):

    @classmethod
    def setUpClass(cls):
        super(RedisLibraryAuthFailTest, cls).setUpClass()
        cls.redis.config_set('REQUIREPASS', 'password')
        cls.redis = Redis(host='localhost', port=6379, db=0)
        try:
            cls.redis.execute_command('AUTH wrong_password')
        except ResponseError:
            pass

    @classmethod
    def tearDownClass(cls):
        cls.redis = Redis(host='localhost', port=6379, db=0)
        cls.redis.execute_command('AUTH password')
        cls.redis.config_set('REQUIREPASS', '')
        cls.redis = Redis(host='localhost', port=6379, db=0)
        super(RedisLibraryAuthFailTest, cls).tearDownClass()

    def test_get(self):
        self.assertRaises(ResponseError, self.redis.get, 'test_dummy')

    def test_set(self):
        self.assertRaises(ResponseError, self.redis.set, 'test_dummy', 'test_dummy')
