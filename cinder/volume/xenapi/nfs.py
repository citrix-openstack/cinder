from cinder import flags
from cinder.openstack.common import cfg
from cinder.volume.xenapi import lib


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

nfs_opts = [
    cfg.StrOpt('xenapi_nfs_server',
               default=None,
               help='NFS server to be used by XenAPINFSDriver'),
    cfg.StrOpt('xenapi_nfs_serverpath',
               default=None,
               help='Path of exported NFS, used by XenAPINFSDriver'),
]

FLAGS = flags.FLAGS
FLAGS.register_opts(xenapi_opts)
FLAGS.register_opts(nfs_opts)


class XenAPINFSOperations(object):
    def __init__(self):
        self.session_factory = lib.SessionFactory(
            FLAGS.xenapi_connection_url,
            FLAGS.xenapi_connection_username,
            FLAGS.xenapi_connection_password
        )

    def create_volume(self, size, name, desc):
        ''' Create the volume, and return with a dict containing
        provider_location
        '''
        with self._session_factory.get_session() as session:
            host_ref = session.get_this_host()
            with session.new_sr_on_nfs(host_ref, server, serverpath) as sr_ref:
                sr_uuid = session.get_sr_uuid(sr_ref)
                vdi_ref = session.create_new_vdi(sr_ref, size)
                vdi_uuid = session.get_vdi_uuid(vdi_ref)

            return dict(
                sr_uuid=sr_uuid,
                vdi_uuid=vdi_uuid,
                server=server,
                serverpath=serverpath)

    def _stuff(self):
        session_factory = xenapi_lib.SessionFactory(
            FLAGS.xenapi_connection_url,
            FLAGS.xenapi_connection_username,
            FLAGS.xenapi_connection_password
        )
