from cinder import flags
from cinder.openstack.common import cfg


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
        pass

    def create_volume(self, size):
        ''' Create the volume, and return with a dict containing
        provider_location
        provider_auth (maybe)
        display_name
        display_description
        '''
        pass

    def _stuff(self):
        session_factory = xenapi_lib.SessionFactory(
            FLAGS.xenapi_connection_url,
            FLAGS.xenapi_connection_username,
            FLAGS.xenapi_connection_password
        )
