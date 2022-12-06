# coding: utf-8
import telnetlib
import unittest
from tests.dbclient import MCStore
from tests.base import BeansdbInstance, get_server_addr, BaseTest


class AbnormalCmdTest(BaseTest):
    def setUp(self):
        BaseTest.setUp(self)
        self.store = MCStore(self.db.addr)
        self.invalid_key = str.encode('/this/is/a/bad/key/%s' % chr(15))

    def run_cmd_by_telnet(self, cmd, expected, timeout=2):
        addr, port = self.db.addr.split(':')
        t = telnetlib.Telnet(addr, port)
        t.write(str.encode('%s\r\n' % cmd))
        out = t.read_until(b'\n', timeout=timeout)
        t.write(b'quit\n')
        t.close()
        r = out.strip(b'\r\n')
        self.assertEqual(bytes.decode(r), expected)

    def test_get(self):
        # get not exist key
        cmd = 'get /test/get'
        self.run_cmd_by_telnet(cmd, 'END')

        # invalid key
        cmd = 'get %s' % self.invalid_key
        self.run_cmd_by_telnet(cmd, 'END')
        self.checkCounterZero()

    def test_set(self):
        # invalid key
        cmd = 'set %s 0 0 3\r\naaa' % self.invalid_key
        self.run_cmd_by_telnet(cmd, 'NOT_STORED')

        cmd = 'set /test/set 0 0 3\r\naaaa'
        self.run_cmd_by_telnet(cmd, 'CLIENT_ERROR bad data chunk')
        self.checkCounterZero()

    def test_incr(self):
        key = '/test/incr'
        self.assertEqual(self.store.delete(key), True)
        cmd = 'incr %s 10' % key
        self.run_cmd_by_telnet(cmd, '10')
        self.assertEqual(self.store.get(key), 10)

        # incr 一个 value 为字符串的 key
        key = '/test/incr2'
        self.assertEqual(self.store.set(key, 'aaa'), True)
        cmd = 'incr %s 10' % key
        self.run_cmd_by_telnet(cmd, '0')
        self.assertEqual(self.store.get(key), 'aaa')
        self.checkCounterZero()

    def test_delete(self):
        key = '/delete/not/exist/key'
        cmd = str.encode('delete %s' % key)
        self.run_cmd_by_telnet(cmd, 'NOT_FOUND')

        cmd = str.encode('delete %s' % self.invalid_key)
        self.run_cmd_by_telnet(cmd, 'NOT_FOUND')
        self.checkCounterZero()

    def test_get_meta_by_key(self):
        key = '/get_meta_by_key/not/exist/key'
        cmd = 'get ?%s' % key
        self.run_cmd_by_telnet(cmd, 'END')

        cmd = 'get ?%s' % self.invalid_key
        self.run_cmd_by_telnet(cmd, 'END')
        self.checkCounterZero()
