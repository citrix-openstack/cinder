# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import pickle

from cinder import flags
from cinder.image import glance
from cinder.openstack.common import cfg
from cinder.openstack.common import log as logging
from cinder.volume import driver
from cinder.volume.drivers.xenapi import lib as xenapi_lib


LOG = logging.getLogger(__name__)

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
        self.nova_plugins = xenapi_lib.NovaPlugins(session_factory)

    def create_cloned_volume(self, volume, src_vref):
        raise NotImplementedError()

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

    def initialize_connection(self, volume, connector):
        sr_uuid, vdi_uuid = volume['provider_location'].split('/')

        return dict(
            driver_volume_type='xensm',
            data=dict(
                name_label=volume['display_name'] or '',
                name_description=volume['display_description'] or '',
                sr_uuid=sr_uuid,
                vdi_uuid=vdi_uuid,
                sr_type='nfs',
                server=FLAGS.xenapi_nfs_server,
                serverpath=FLAGS.xenapi_nfs_serverpath,
                introduce_sr_keys=['sr_type', 'server', 'serverpath']
            )
        )

    def terminate_connection(self, volume, connector, force=False, **kwargs):
        pass

    def check_for_setup_error(self):
        """To override superclass' method"""

    def create_volume_from_snapshot(self, volume, snapshot):
        return self._copy_volume(
            snapshot, volume['display_name'], volume['name_description'])

    def create_snapshot(self, snapshot):
        volume_id = snapshot['volume_id']
        volume = snapshot['volume']
        return self._copy_volume(
            volume, snapshot['display_name'], snapshot['display_description'])

    def _copy_volume(self, volume, target_name, target_desc):
        sr_uuid, vdi_uuid = volume['provider_location'].split('/')

        volume_details = self.nfs_ops.copy_volume(
            FLAGS.xenapi_nfs_server,
            FLAGS.xenapi_nfs_serverpath,
            sr_uuid,
            vdi_uuid,
            target_name,
            target_desc
        )
        location = "%(sr_uuid)s/%(vdi_uuid)s" % volume_details
        return dict(provider_location=location)

    def delete_snapshot(self, snapshot):
        self.delete_volume(snapshot)

    def ensure_export(self, context, volume):
        pass

    def copy_image_to_volume(self, context, volume, image_service, image_id):
        sr_uuid, vdi_uuid = volume['provider_location'].split('/')

        uuid_stack = [vdi_uuid]

        api_servers = glance.get_api_servers()
        glance_host, glance_port, glance_use_ssl = api_servers.next()
        auth_token = context.auth_token

        plugin_kwargs = dict(
            image_id=image_id,
            glance_host=glance_host,
            glance_port=glance_port,
            glance_use_ssl=glance_use_ssl,
            uuid_stack=uuid_stack,
            sr_path="/var/run/sr-mount/" + sr_uuid,
            auth_token=auth_token)

        plugin_params = dict(args=[], kwargs=plugin_kwargs)

        args = dict(params=pickle.dumps(plugin_params))

        self.nfs_ops.connect_volume(
            FLAGS.xenapi_nfs_server,
            FLAGS.xenapi_nfs_serverpath,
            sr_uuid,
            vdi_uuid)

        try:
            # TODO(matelakat): pickle.loads result
            self.nova_plugins.call_plugin('glance', 'download_vhd', args)
        except xenapi_lib.XenAPIException as e:
            LOG.error("Failed to call glance xenapi plugin. Make sure, " +
                      "that the glance XenAPI plugin is installed on host " +
                      FLAGS.xenapi_connection_url)
            raise
        finally:
            self.nfs_ops.disconnect_volume(vdi_uuid)

        self.nfs_ops.resize_volume(
            FLAGS.xenapi_nfs_server,
            FLAGS.xenapi_nfs_serverpath,
            sr_uuid,
            vdi_uuid,
            volume['size'])

    def copy_volume_to_image(self, context, volume, image_service, image_meta):
        raise NotImplementedError()
