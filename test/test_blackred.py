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


import unittest
import blackred
import redis


class BlackRedTest(unittest.TestCase):

    r = None

    @classmethod
    def setUpClass(cls):
        """
        Create a redis test connection for validation
        """
        cls.r = redis.Redis(host='localhost', port=6379, db=0)
        """:type: redis.Redis"""

    @classmethod
    def tearDownClass(cls):
        """
        Clean up the redis database
        """
        for victim in ['127.0.0.1', '127.0.0.2', '127.0.0.3', '127.0.0.4', '127.0.0.5', '127.0.0.6', '127.0.0.7']:
            cls.r.delete('BlackRed:WatchList:' + victim)
            cls.r.delete('BlackRed:BlackList:' + victim)

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

    def test_check_blacklisted(self):
        br = blackred.BlackRed()
        victim = '127.0.0.5'
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
        self.assertIsNone(value)
        value = br.get_blacklist_ttl(item)
        self.assertLessEqual(value, 86400)
        self.assertGreater(value, 86398)
