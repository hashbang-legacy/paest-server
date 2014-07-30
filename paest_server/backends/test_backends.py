# -*- coding: utf-8 -*-

import unittest
import redisimpl
import testimpl
from testutils import redis_server


class BackendTests(object):

    @classmethod
    def setUpDB(cls):
        raise NotImplementedError("setUpDB not implemented")

    @classmethod
    def tearDownDB(cls):
        pass

    @classmethod
    def setUpClass(cls):
       cls.db = cls.setUpDB()

    @classmethod
    def tearDownClass(cls):
        cls.tearDownDB()

    # Create methods
    def test_create_handles_collisions(self):
        paest = self.db.create_paest("id", "key", "content")
        paest2 = self.db.create_paest("id", "key2", "content2")
        self.assertNotEqual(paest.pid, paest2.pid)
# Generally, there's no such thing as a 'bad' id or key.
#    def test_create_handles_bad_ids(self):
#        bad_id = "!@#$:"
#        paest = self.db.create_paest(bad_id, "key", "content")
#        self.assertNotEqual(bad_id, paest.pid)
#
#    def test_create_handles_bad_keys(self):
#        pid = "TeCrHaBaKe"
#        bad_key = "!@#$:"
#        paest = self.db.create_paest(pid, bad_key, "content")
#        self.assertNotEqual(bad_key, paest.key)

    def test_create_provides_defaults(self):
        paest = self.db.create_paest("", "", "")
        self.assertNotEqual("", paest.pid)
        self.assertNotEqual("", paest.key)
        self.assertEqual("", paest.content)

    # Get methods
    def test_failed_get_returns_none(self):
        self.assertEqual(None, self.db.get_paest("missing"))

    def test_get_returns_paest(self):
        pid = "TeGeRePa"
        content = "paest content"
        self.db.create_paest(pid, "", content)
        paest = self.db.get_paest(pid)
        self.assertEqual(content, paest.content)

    # Update methods
    def test_update(self):
        pid = "TeUp"
        content = "Paest Content"
        content2 = "other content"

        paest = self.db.create_paest(pid, "", content)

        self.assertTrue(self.db.update_paest(paest.pid,
                                                 paest.key,
                                                 content2))
        self.assertEqual(content2, self.db.get_paest(paest.pid).content)

    def test_update_fails_on_bad_key(self):
        pid = "TeUpFaOnBaKe"
        content = "Paest content"
        content2 = "other content"

        paest = self.db.create_paest(pid, "", content)

        self.assertFalse(self.db.update_paest(paest.pid,
                                                  "BadKey",
                                                  content2))
        self.assertEqual(content, self.db.get_paest(paest.pid).content)

    def test_update_fails_on_bad_id(self):
        pid = "TeUpFaOnBaId"
        content = "Paest content"
        content2 = "other content"

        paest = self.db.create_paest(pid, "", content)

        self.assertFalse(self.db.update_paest("badid",
                                                  paest.key,
                                                  content2))
        self.assertEqual(content, self.db.get_paest(paest.pid).content)

    # Delete methods
    def test_delete(self):
        pid = "TeDe"
        content = "Paest content"

        paest = self.db.create_paest(pid, "", content)

        self.assertTrue(self.db.delete_paest(pid, paest.key))
        self.assertEqual(None, self.db.get_paest(pid))

    def test_delete_fails_on_bad_key(self):
        pid = "TeDeFaOnBaKe"
        content = "Paest content"

        paest = self.db.create_paest(pid, "", content)

        self.assertFalse(self.db.delete_paest(pid, "badKey"))
        self.assertEqual(content, self.db.get_paest(pid).content)

    def test_delete_fails_on_bad_id(self):
        pid = "TeDeFaOnBaId"
        content = "Paest content"

        paest = self.db.create_paest(pid, "", content)

        self.assertFalse(self.db.delete_paest("badId", paest.key))
        self.assertEqual(content, self.db.get_paest(pid).content)

    def test_handles_unicode(self):
        pid = "TeUn"
        content = u" broken        │00:21:01 musegarden | eeeee!    "

        self.db.create_paest(pid, "", content)

        paest = self.db.get_paest(pid)
        self.assertEqual(content, paest.content)


class TestRedisImpl(BackendTests, unittest.TestCase):
    @classmethod
    def setUpDB(cls):
        cls.server = redis_server.RedisServer(1025)
        return redisimpl.RedisDB(port=1025)

    @classmethod
    def tearDownDB(cls):
        cls.server.stop()

class TestTestImpl(BackendTests, unittest.TestCase):

    @classmethod
    def setUpDB(cls):
        return testimpl.TestDB()

