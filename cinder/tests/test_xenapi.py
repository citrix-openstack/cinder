from cinder.volume import driver
from cinder.volume.xenapi import nfs
import unittest
import mox


class DriverTestCase(unittest.TestCase):
    def test_do_setup_delegation(self):
        mock = mox.Mox()
        mock.StubOutWithMock(driver.xenapi_nfs, 'XenAPINFSOperations')
        driver.xenapi_nfs.XenAPINFSOperations().AndReturn('xenapi_nfs')
        drv = driver.XenAPINFSDriver()

        mock.ReplayAll()
        drv.do_setup('context')
        mock.VerifyAll()

        self.assertEquals('xenapi_nfs', drv.xenapi_nfs)

    def test_create_volume_delegation(self):
        mock = mox.Mox()

        ops = mock.CreateMock(nfs.XenAPINFSOperations)
        drv = driver.XenAPINFSDriver()
        drv.xenapi_nfs = ops

        ops.create_volume(1).AndReturn('result')

        mock.ReplayAll()
        result = drv.create_volume(dict(size=1))
        mock.VerifyAll()

        self.assertEquals('result', result)

    def _ignore(self):
        mock = mox.Mox()
        mock.StubOutWithMock(driver.xenapi_nfs, 'XenAPINFSOperations')
        mock.StubOutWithMock(driver, 'FLAGS')
        drv = driver.XenAPINFSDriver()
        driver.FLAGS.xenapi_connection_url = 'url'
        driver.FLAGS.xenapi_connection_username = 'user'
        driver.FLAGS.xenapi_connection_password = 'pass'

        driver.xenapi.SessionFactory('url', 'user', 'pass').AndReturn('sf')
        driver.xenapi.XenAPINFSOperations('sf').AndReturn('xenapi_nfs')

        mock.ReplayAll()
        drv.do_setup('context')
        mock.VerifyAll()

        self.assertEquals('xenapi_nfs', drv.xenapi_nfs)


