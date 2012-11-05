import unittest
import mox
from cinder.volume.xenapi import nfs


class InitTestCase(unittest.TestCase):
    def test_session_factory_created(self):
        mock = mox.Mox()
        mock.StubOutWithMock(nfs.lib, 'SessionFactory')
        mock.StubOutWithMock(nfs, 'FLAGS')
        nfs.FLAGS.xenapi_connection_url = 'url'
        nfs.FLAGS.xenapi_connection_username = 'user'
        nfs.FLAGS.xenapi_connection_password = 'pass'
        nfs.lib.SessionFactory('url', 'user', 'pass').AndReturn('sf')

        mock.ReplayAll()
        ops = nfs.XenAPINFSOperations()
        mock.VerifyAll()

        self.assertEquals('sf', ops.session_factory)
