from cinder import flags
from cinder.openstack.common import cfg
from cinder.volume.xenapi import lib
import json


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