from cinder import flags
from cinder.openstack.common import cfg
from cinder.volume import driver
from cinder.volume.xenapi import lib as xenapi_lib


xenapi_opts = [
    cfg.StrOpt('xenapi_connection_url',
               default=None,
               help='URL for XenAPI connection'),
    cfg.StrOpt('xenapi_connection_username',
               default='root',
               help='Username for XenAPI connection'),
    cfg.StrOpt('xenapi_connection_password',
               default=None,
               help='Password for XenAPI connection'),
]

xenapi_nfs_opts = [
    cfg.StrOpt('xenapi_nfs_server',
               default=None,
               help='NFS server to be used by XenAPINFSDriver'),
    cfg.StrOpt('xenapi_nfs_serverpath',
               default=None,
               help='Path of exported NFS, used by XenAPINFSDriver'),
]

FLAGS = flags.FLAGS
FLAGS.register_opts(xenapi_opts)
FLAGS.register_opts(xenapi_nfs_opts)


class XenAPINFSDriver(driver.VolumeDriver):

    def do_setup(self, context):
        session_factory = xenapi_lib.SessionFactory(
            FLAGS.xenapi_connection_url,
            FLAGS.xenapi_connection_username,
            FLAGS.xenapi_connection_password
        )
        self.nfs_ops = xenapi_lib.NFSBasedVolumeOperations(session_factory)

    def create_volume(self, volume):
        volume_details = self.nfs_ops.create_volume(
            FLAGS.xenapi_nfs_server,
            FLAGS.xenapi_nfs_serverpath,
            volume['size'],
            volume['display_name'],
            volume['display_description']
        )
        location = "%(sr_uuid)s/%(vdi_uuid)s" % volume_details
        return dict(provider_location=location)

    def create_export(self, context, volume):
        pass

    def delete_volume(self, volume):
        sr_uuid, vdi_uuid = volume['provider_location'].split('/')
        self.nfs_ops.delete_volume(
            FLAGS.xenapi_nfs_server,
            FLAGS.xenapi_nfs_serverpath,
            sr_uuid,
            vdi_uuid
        )

    def remove_export(self, context, volume):
        pass

    def check_for_setup_error(self):
        """To override superclass' method"""

    def initialize_connection(self, volume, connector):
        """Allow connection to connector and return connection info."""
        raise NotImplementedError()

    def create_volume_from_snapshot(self, volume, snapshot):
        raise NotImplementedError()

    def create_snapshot(self, snapshot):
        raise NotImplementedError()

    def delete_snapshot(self, snapshot):
        raise NotImplementedError()
