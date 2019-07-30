"""
Copyright 2016 Juergen Edelbluth

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

import redis

import blackred
import blackred.blackred as blackred_util

__author__ = 'Juergen Edelbluth'


class BlackRedTestWithoutAuthentication(unittest.TestCase):

    r = None
    """:type: redis.Redis"""

    @classmethod
    def setUpClass(cls):
        """
        Create a redis test connection for validation
        """
        cls.r = redis.Redis(host='localhost', port=6379, db=0)

    @classmethod
    def tearDownClass(cls):
        """
        Clean up the redis database
        """
        cls.r.flushdb()

    def setUp(self):
        blackred.BlackRed.Settings.ANONYMIZATION = False
        blackred.BlackRed.Settings.REDIS_USE_SOCKET = False

    def tearDown(self):
        blackred.BlackRed.Settings.ANONYMIZATION = False
        blackred.BlackRed.Settings.REDIS_USE_SOCKET = False

    def test_misconnect(self):
        br = blackred.BlackRed(redis_port=1)
        self.assertRaises(redis.exceptions.ConnectionError, br.is_not_blocked, 'test')

    def test_check_ok(self):
        br = blackred.BlackRed()
        victim = '127.0.0.1'
        self.assertTrue(br.is_not_blocked(victim))

    def test_fail(self):
        br = blackred.BlackRed()
        victim = '127.0.0.2'
        br.log_fail(victim)
        value = self.r.get('BlackRed:WatchList:' + victim)
        self.assertIsNotNone(value)
        self.assertEqual(1, int(value))
        value = self.r.get('BlackRed:BlackList:' + victim)
        self.assertIsNone(value)
        self.assertTrue(br.is_not_blocked(victim))
        self.assertFalse(br.is_blocked(victim))

    def test_double_fail(self):
        br = blackred.BlackRed()
        victim = '127.0.0.3'
        br.log_fail(victim)
        br.log_fail(victim)
        value = self.r.get('BlackRed:WatchList:' + victim)
        self.assertIsNotNone(value)
        self.assertEqual(2, int(value))
        value = self.r.get('BlackRed:BlackList:' + victim)
        self.assertIsNone(value)
        self.assertTrue(br.is_not_blocked(victim))
        self.assertFalse(br.is_blocked(victim))

    def test_triple_fail(self):
        br = blackred.BlackRed()
        victim = '127.0.0.4'
        br.log_fail(victim)
        br.log_fail(victim)
        br.log_fail(victim)
        value = self.r.get('BlackRed:WatchList:' + victim)
        self.assertIsNone(value)
        value = self.r.get('BlackRed:BlackList:' + victim)
        self.assertIsNotNone(value)
        self.assertFalse(br.is_not_blocked(victim))

    def test_check_blacklisted_blocked(self):
        br = blackred.BlackRed()
        victim = '127.0.0.5'
        br.log_fail(victim)
        br.log_fail(victim)
        br.log_fail(victim)
        self.assertTrue(br.is_blocked(victim))

    def test_check_blacklisted_notblocked(self):
        br = blackred.BlackRed()
        victim = '127.0.0.12'
        br.log_fail(victim)
        br.log_fail(victim)
        br.log_fail(victim)
        self.assertFalse(br.is_not_blocked(victim))

    def test_unblock(self):
        br = blackred.BlackRed()
        victim = '127.0.0.6'
        br.log_fail(victim)
        br.log_fail(victim)
        br.log_fail(victim)
        self.assertFalse(br.is_not_blocked(victim))
        br.unblock(victim)
        self.assertTrue(br.is_not_blocked(victim))
        value = self.r.get('BlackRed:WatchList:' + victim)
        self.assertIsNone(value)
        value = self.r.get('BlackRed:BlackList:' + victim)
        self.assertIsNone(value)

    def test_assert_is_blocked(self):
        br = blackred.BlackRed()
        self.assertRaises(AssertionError, br.is_blocked, None)

    def test_assert_is_not_blocked(self):
        br = blackred.BlackRed()
        self.assertRaises(AssertionError, br.is_not_blocked, None)

    def test_assert_log_fail(self):
        br = blackred.BlackRed()
        self.assertRaises(AssertionError, br.log_fail, None)

    def test_assert_unblock(self):
        br = blackred.BlackRed()
        self.assertRaises(AssertionError, br.unblock, None)

    def test_assert_encode(self):
        br = blackred.BlackRed()
        self.assertRaises(AssertionError, br._encode_item, None)

    def test_assert_watchlist_ttl(self):
        br = blackred.BlackRed()
        self.assertRaises(AssertionError, br.get_watchlist_ttl, None)

    def test_assert_blacklist_ttl(self):
        br = blackred.BlackRed()
        self.assertRaises(AssertionError, br.get_blacklist_ttl, None)

    def test_ttl_check(self):
        item = '127.0.0.7'
        br = blackred.BlackRed()
        br.log_fail(item)
        value = br.get_watchlist_ttl(item)
        self.assertLessEqual(value, 180)
        self.assertGreater(value, 178)
        br.log_fail(item)
        br.log_fail(item)
        value = br.get_watchlist_ttl(item)
        self.assertEqual(value, -2)
        value = br.get_blacklist_ttl(item)
        self.assertLessEqual(value, 86400)
        self.assertGreater(value, 86398)

    def test_item_representation(self):
        item = '127.0.0.8'
        br = blackred.BlackRed()
        item_encoded = br._encode_item(item)
        self.assertIsNotNone(item_encoded)
        self.assertEqual(item, item_encoded)
        blackred.BlackRed.Settings.ANONYMIZATION = True
        br = blackred.BlackRed()
        item_encoded = br._encode_item(item)
        self.assertIsNotNone(item_encoded)
        self.assertNotEqual(item, item_encoded)

    def test_anonymization(self):
        item = '127.0.0.9'
        br = blackred.BlackRed()
        br.log_fail(item)
        value = self.r.get(blackred.BlackRed.Settings.WATCHLIST_KEY_TEMPLATE.format(item))
        self.assertIsNotNone(value)
        value = int(value)
        self.assertEqual(value, 1)
        blackred.BlackRed.Settings.ANONYMIZATION = True
        br = blackred.BlackRed()
        br.log_fail(item)
        # basically, check if it did not hit the same key
        value = self.r.get(blackred.BlackRed.Settings.WATCHLIST_KEY_TEMPLATE.format(item))
        self.assertIsNotNone(value)
        value = int(value)
        self.assertEqual(value, 1)

    def test_salt(self):
        salt = blackred_util.create_salt()
        self.assertIsNotNone(salt)
        self.assertIsInstance(salt, bytes)
        self.assertEqual(len(salt), 128)
        salt = blackred_util.create_salt(256)
        self.assertIsNotNone(salt)
        self.assertIsInstance(salt, bytes)
        self.assertEqual(len(salt), 256)

    def test_anon_triple_fail(self):
        blackred.BlackRed.Settings.ANONYMIZATION = True
        br = blackred.BlackRed()
        victim = '127.0.0.10'
        br.log_fail(victim)
        self.assertFalse(br.is_blocked(victim))
        value = self.r.get('BlackRed:WatchList:' + victim)
        self.assertIsNone(value)
        value = self.r.get('BlackRed:BlackList:' + victim)
        self.assertIsNone(value)
        br.log_fail(victim)
        self.assertFalse(br.is_blocked(victim))
        value = self.r.get('BlackRed:WatchList:' + victim)
        self.assertIsNone(value)
        value = self.r.get('BlackRed:BlackList:' + victim)
        self.assertIsNone(value)
        br.log_fail(victim)
        self.assertFalse(br.is_not_blocked(victim))
        value = self.r.get('BlackRed:WatchList:' + victim)
        self.assertIsNone(value)
        value = self.r.get('BlackRed:BlackList:' + victim)
        self.assertIsNone(value)

    def test_log_fail_on_blocked(self):
        br = blackred.BlackRed()
        victim = '127.0.0.11'
        br.log_fail(victim)
        br.log_fail(victim)
        br.log_fail(victim)
        self.assertTrue(br.is_blocked(victim))
        br.log_fail(victim)
        self.assertTrue(br.is_blocked(victim))

    def test_socket_connection_fail_predef(self):
        blackred.BlackRed.Settings.REDIS_USE_SOCKET = True
        br = blackred.BlackRed()
        self.assertRaises(redis.ConnectionError, br.is_blocked, '127.0.0.13')

    def test_socket_connection_fail_init(self):
        br = blackred.BlackRed(redis_use_socket=True)
        self.assertRaises(redis.ConnectionError, br.is_blocked, '127.0.0.14')


class BlackRedTestWithAuthentication(BlackRedTestWithoutAuthentication):

    @classmethod
    def setUpClass(cls):
        super(BlackRedTestWithAuthentication, cls).setUpClass()
        cls.r.config_set('REQUIREPASS', 'password')
        cls.r = redis.Redis(host='localhost', port=6379, db=0)
        cls.r.execute_command('AUTH password')

    @classmethod
    def tearDownClass(cls):
        cls.r.config_set('REQUIREPASS', '')
        cls.r = redis.Redis(host='localhost', port=6379, db=0)
        super(BlackRedTestWithAuthentication, cls).tearDownClass()

    def setUp(self):
        blackred.BlackRed.Settings.ANONYMIZATION = False
        blackred.BlackRed.Settings.REDIS_USE_SOCKET = False
        blackred.BlackRed.Settings.REDIS_AUTH = 'password'

    def tearDown(self):
        blackred.BlackRed.Settings.REDIS_AUTH = None
        blackred.BlackRed.Settings.ANONYMIZATION = False
        blackred.BlackRed.Settings.REDIS_USE_SOCKET = False

    def test_invalid_password(self):
        blackred.BlackRed.Settings.REDIS_AUTH = 'wrong_password!'
        br = blackred.BlackRed()
        self.assertRaises(redis.exceptions.AuthenticationError, br.log_fail, 'something')
