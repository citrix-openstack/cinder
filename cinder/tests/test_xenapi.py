from cinder.volume import driver
from cinder.volume.xenapi import lib
import unittest
import mox


class DriverTestCase(unittest.TestCase):

    def assert_flag(self, flagname):
        self.assertTrue(hasattr(driver.FLAGS, flagname))

    def test_config_options(self):
        self.assert_flag('xenapi_connection_url')
        self.assert_flag('xenapi_connection_username')
        self.assert_flag('xenapi_connection_password')
        self.assert_flag('xenapi_nfs_server')
        self.assert_flag('xenapi_nfs_serverpath')

    def test_do_setup(self):
        mock = mox.Mox()
        mock.StubOutWithMock(driver, 'xenapi_lib')
        mock.StubOutWithMock(driver, 'FLAGS')

        driver.FLAGS.xenapi_connection_url = 'url'
        driver.FLAGS.xenapi_connection_username = 'user'
        driver.FLAGS.xenapi_connection_password = 'pass'

        session_factory = object()
        nfsops = object()

        driver.xenapi_lib.SessionFactory('url', 'user', 'pass').AndReturn(
            session_factory)

        driver.xenapi_lib.NFSBasedVolumeOperations(
            session_factory).AndReturn(nfsops)

        drv = driver.XenAPINFSDriver()

        mock.ReplayAll()
        drv.do_setup('context')
        mock.VerifyAll()

        self.assertEquals(nfsops, drv.nfs_ops)

    def test_create_volume(self):
        mock = mox.Mox()

        mock.StubOutWithMock(driver, 'FLAGS')
        driver.FLAGS.xenapi_nfs_server = 'server'
        driver.FLAGS.xenapi_nfs_serverpath = 'path'

        ops = mock.CreateMock(lib.NFSBasedVolumeOperations)
        drv = driver.XenAPINFSDriver()
        drv.nfs_ops = ops

        ops.create_volume(
            'server', 'path', 1, 'name', 'desc').AndReturn('result')

        mock.ReplayAll()
        result = drv.create_volume(dict(
            size=1, display_name='name', display_description='desc'))
        mock.VerifyAll()

        self.assertEquals(dict(
                metadata='result'
            ), result)
