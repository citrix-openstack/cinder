from cinder.volume import driver
import unittest
import mox


class DriverDoSetupTestCase(unittest.TestCase):
    def test_xenapi_nfs_init(self):
        mock = mox.Mox()
        mock.StubOutWithMock(driver.xenapi, 'SessionFactory')
        mock.StubOutWithMock(driver.xenapi, 'XenAPINFSOperations')
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
